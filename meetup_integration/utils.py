import json
import logging
import random
import requests

from datetime import datetime
from itertools import chain

from django.conf import settings

from pytz import utc

from meetup_integration.models import Member, Group, Event, Attendance, RSVP, Team, Season

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


def sync_rsvp(event):
    rsvps = MeetupAPI("2/rsvps", event_id=event.id).get()["results"]
    count = 0

    for rsvp in rsvps:
        obj, created = RSVP.objects.get_or_create(
            id=rsvp["rsvp_id"],
            response=rsvp["response"],
            event=Event.objects.get(id=rsvp["event"]["id"]),
            member=Member.objects.get(id=rsvp["member"]["member_id"]),
        )

        if created:
            count += 1

    return "For event %s, received %d rsvps. Saved %d rsvps." % (event.name, len(rsvps), count)


def team_coef(members, season):
    coefs = [member.win_lose_coefficient(season) for member in members]

    if len(coefs) > 0:
        return float(sum(coefs))/len(coefs)
    else:
        return 0.0


def generate_teams(event, season, no_of_iterations=30):
    coefficients = []
    teams_generated = []
    members = event.get_members_with_rsvp()

    # divide into two groups
    for i in range(no_of_iterations):
        random.shuffle(members)

        team_a = members[len(members)/2:]
        team_b = members[:len(members)/2]

        team_a_coef = team_coef(team_a, season)
        team_b_coef = team_coef(team_b, season)

        coef = abs(team_a_coef - team_b_coef)

        teams_generated.append((team_a, team_b))
        coefficients.append(coef)

    index = coefficients.index(min(coefficients))

    team_a, team_b = teams_generated[index]

    # sort by coefficient
    team_a.sort(key=lambda member: member.win_lose_coefficient(), reverse=True)
    team_b.sort(key=lambda member: member.win_lose_coefficient(), reverse=True)

    return team_a, team_b


def generate_teams_admin(modeladmin, request, queryset):
    for event in queryset:
        season = Season.objects.get(name=settings.CURRENT_SEASON)
        team_a, team_b = generate_teams(event, season, 100)

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

        modeladmin.message_user(request, "Team A: %s, Team B: %s" % (team_a, team_b))
