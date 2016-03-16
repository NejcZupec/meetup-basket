import json
import logging
import numpy as np
import requests

from datetime import datetime
from itertools import chain, combinations
from math import fabs, ceil

from django.conf import settings

from pytz import utc

from meetup_integration.models import Member, Event, Attendance, RSVP, Team, Season

logger = logging.getLogger("meetup_basket")


class MeetupAPI(object):
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def generate_url(self):
        arg_string = "?"
        for key, value in self.kwargs.items():
            arg_string += ("&" + str(key) + "=" + str(value))
        return settings.MEETUP_API_URL + self.func + arg_string + "&key=" + settings.MEETUP_API_KEY

    def get(self):
        try:
            url = self.generate_url()
            logger.info("API request: %s" % url)
            r = requests.get(url)
            j = r.json()
            return j
        except requests.exceptions.RequestException as e:
            print e


def sync_members(modeladmin, request, queryset):
    for group in queryset:
        members = MeetupAPI("2/members", group_id=group.id).get()["results"]

        for member in members:
            print json.dumps(member, indent=4)

            Member.objects.get_or_create(
                id=member["id"],
                name=member["name"],
                link=member["link"],
                status=member["status"],
                group=group,
            )


def sync_events_queryset(modeladmin, request, queryset):
    for group in queryset:
        message = sync_events(group)
        modeladmin.message_user(request, message)


def sync_events(group, force_update=False):
    """
    Sync events for a group.
    """
    events = MeetupAPI("2/events", group_id=group.id, status="past").get()["results"]
    events2 = MeetupAPI("2/events", group_id=group.id, status="upcoming").get()["results"]

    events = list(chain(events, events2))

    count_updated = 0
    count_new = 0
    count_basket = 0

    for e in events:
        logger.debug(json.dumps(e, indent=4))

        # ignore all events, except if event's name stars with 'Basketball match'
        event_type = e["name"][:16]
        if event_type == "Basketball match":
            count_basket += 1

            # find out season
            prefix = e["name"].split(" ")[2]
            season = Season.objects.get(slug=prefix.split("#")[0])

            try:
                event = Event.objects.get(id=e["id"])

                if force_update:
                    count_updated += 1

                    event.name = e["name"]
                    event.event_url = e["event_url"]
                    event.group = group
                    event.status = e["status"]
                    event.season = season
                    event.start_date = datetime.utcfromtimestamp(float(e["time"])/1000)
                    event.save()

            except Event.DoesNotExist:
                count_new += 1

                event = Event.objects.create(
                    id=e["id"],
                    name=e["name"],
                    event_url=e["event_url"],
                    group=group,
                    status=e["status"],
                    season=season,
                    start_date=datetime.utcfromtimestamp(float(e["time"])/1000),
                )

    return "For group %s, received %d events (%d basketball matches). Updated %d events. New %d events." % \
           (group.name, len(events), count_basket, int(count_updated), int(count_new))


def sync_attendance_queryset(modeladmin, request, queryset):
    for event in queryset:
        message = sync_attendance(event)
        modeladmin.message_user(request, message)


def sync_attendance(event):
    """
    Sync attendance for an event.
    """

    if event.start_date > datetime.utcnow().replace(tzinfo=utc):
        return "Event %s hasn't started yet." % event.name

    url = str(event.group.url_name) + "/events/" + str(event.id) + "/attendance/"
    attendances = MeetupAPI(url).get()
    count = 0

    for attendance in attendances:
        logger.debug(json.dumps(attendance, indent=4))

        try:
            rsvp = attendance["rsvp"]["response"]
        except Exception as e:
            rsvp = "No RSVP"

        # ignore deleted users
        if attendance["member"]["id"] != 0:
            logger.debug(attendance["member"]["id"])

            obj, created = Attendance.objects.get_or_create(
                attendance=True if str(attendance["status"]) == "attended" else False,
                rsvp=rsvp,
                event=event,
                member=Member.objects.get(id=int(attendance["member"]["id"])),
            )

            if created:
                count += 1

    return "For event %s, received %d attendances. Saved %d attendances." % (event.name, len(attendances), count)


def sync_rsvp_queryset(modeladmin, request, queryset):
    for event in queryset:
        message = sync_rsvp(event)
        modeladmin.message_user(request, message)


def sync_rsvp(event, force_update=False):
    rsvps = MeetupAPI("2/rsvps", event_id=event.id).get()["results"]
    count = 0
    updated = 0

    for rsvp in rsvps:
        try:
            obj = RSVP.objects.get(
                id=rsvp["rsvp_id"],
            )

            if force_update:
                obj.response = rsvp["response"]
                obj.event = Event.objects.get(id=rsvp["event"]["id"])
                obj.member = Member.objects.get(id=rsvp["member"]["member_id"])
                obj.save()
                updated += 1
        except RSVP.DoesNotExist:
            RSVP.objects.create(
                id=rsvp["rsvp_id"],
                response=rsvp["response"],
                event=Event.objects.get(id=rsvp["event"]["id"]),
                member=Member.objects.get(id=rsvp["member"]["member_id"]),
            )
            count += 1

    return "For event %s, received %d rsvps. Saved %d rsvps. Updated %d rsvps." % \
           (event.name, len(rsvps), count, updated)


def team_weights(members, season):
    games_played = [member.games_played(season) for member in members]
    all_games_played = float(sum(games_played))
    return [gp/all_games_played for gp in games_played]


def team_coef_weighted(members, season):
    """
    Team coefficients are weighted by games played.
    """
    weights = team_weights(members, season)
    coefs = [member.win_lose_coefficient(season) for member in members]
    return float(np.dot(np.array(weights), np.array(coefs)))


def team_diff_avg(members, season):
    """
    Team average diffs are wighted by games played.
    """
    weights = team_weights(members, season)
    avg_diffs = [member.basket_diff_avg(season) for member in members]
    return float(np.dot(np.array(weights), np.array(avg_diffs)))


def seperate_teams(members, a_team):
    """
    members = all members
    a_team = only a_team members
    b_team = members - a_team
    """
    a_team = a_team[:]
    for m in a_team:
        members.remove(m)
    return a_team, members


def generate_teams(event, season=Season.objects.get(name=settings.CURRENT_SEASON), combination=None):
    members = event.get_members_with_rsvp()

    logger.info("%d players RSVPed with yes for event %s." % (len(members), event))
    members_in_one_group = int(ceil(len(members)/2.0))
    logger.info("Players in 1 group: %d" % members_in_one_group)
    combs = list(combinations(members, members_in_one_group))
    logger.info("All combinations of groups: %d" % len(combs))

    if combination:
        logger.info("Use combination %d." % int(combination))

    possible_combs = []

    for c in combs:
        a_team, b_team = seperate_teams(event.get_members_with_rsvp(), c)

        a_team_avg_height = sum([m.height for m in a_team])*1.0/len(a_team)
        b_team_avg_height = sum([m.height for m in b_team])*1.0/len(b_team)
        diff = fabs(a_team_avg_height - b_team_avg_height)

        if diff <= settings.MAX_HEIGHT_DIFF:
            possible_combs.append({"a": a_team, "b": b_team})

    logger.info("Possible height combinations (max height diff: %d cm): %d" % (settings.MAX_HEIGHT_DIFF, len(possible_combs)))

    if len(possible_combs) == 0:
        logger.warning("No possible combinations. Check if you have already synced RSVPs.")
        return [], []

    results = []

    # divide into two groups
    for i in range(len(possible_combs)):
        team_a = possible_combs[i]["a"]
        team_b = possible_combs[i]["b"]

        diff_avg_diff = abs(team_diff_avg(team_a, season) - team_diff_avg(team_b, season))
        diff_coef = abs(team_coef_weighted(team_a, season) - team_coef_weighted(team_b, season))

        results.append({
            "diff_avg_diff": diff_avg_diff,
            "diff_coef": diff_coef,
            "team_a": team_a,
            "team_b": team_b,
            "diff_sum": diff_avg_diff + 10*diff_coef
        })

    sorted_results = sorted(results, key=lambda e: e["diff_sum"])

    print "coef_avg diff.\t coef diff.\t sum"

    for i, c in enumerate(sorted_results[:15]):
        print "---------------------- Combination %d -------------------" % i
        print c["diff_avg_diff"], c["diff_coef"], c["diff_sum"]
        print "Team A:",
        for m in c["team_a"]:
            print m.name[:7] + ";",
        print
        print "Team B:",
        for m in c["team_b"]:
            print m.name[:7] + ";",
        print

    r = combination if combination else 0

    logger.info("Combination selected: %d" % r)

    team_a = sorted_results[r]["team_a"]
    team_b = sorted_results[r]["team_b"]

    return team_a, team_b


def generate_teams_admin(modeladmin, request, queryset):
    for event in queryset:
        message = generate_teams_for_event(event)
        modeladmin.message_user(request, message)


def generate_teams_for_event(event, combination=None):
    season = Season.objects.get(name=settings.CURRENT_SEASON)
    team_a, team_b = generate_teams(event, season, combination=combination)

    # delete old teams for current event
    Team.objects.filter(event=event).delete()

    # team A
    a = Team.objects.create(name="A", event=event)

    for member in team_a:
        a.members.add(member)
    a.save()

    # team B
    b = Team.objects.create(name="B", event=event)

    for member in team_b:
        b.members.add(member)
    b.save()

    return "Team A: %s, Team B: %s" % ([m.name for m in team_a], [m.name for m in team_b])
