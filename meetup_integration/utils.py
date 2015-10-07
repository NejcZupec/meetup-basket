import json
import logging
import random
import requests

from django.conf import settings

from meetup_integration.models import Member, Group, Event, Attendance, RSVP, Team

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
            return r.json()
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


def sync_events(group):
    """
    Sync events for a group.
    """
    events = MeetupAPI("2/events", group_id=group.id, status="past").get()["results"]

    count_updated = 0

    for event in events:
        logger.debug(json.dumps(event, indent=4))

        # ignore all events, except if event's name stars with 'Basketball match'
        event_type = event["name"][:16]
        if event_type == "Basketball match":
            event, created = Event.objects.get_or_create(
                id=event["id"],
                name=event["name"],
                event_url=event["event_url"],
                group=group,
                status=event["status"],
            )

            if created:
                count_updated

    return "For group %s, received %d events. Updated %d events." % (group.name, len(events), int(count_updated))


def sync_attendance(modeladmin, request, queryset):
    for event in queryset:
        url = str(event.group.url_name) + "/events/" + str(event.id) + "/attendance/"
        print url
        attendances = MeetupAPI(url).get()
        count = 0

        for attendance in attendances:
            print json.dumps(attendance, indent=4)

            try:
                rsvp = attendance["rsvp"]["response"]
            except Exception as e:
                rsvp = "No RSVP"

            # ignore deleted users
            if attendance["member"]["id"] != 0:
                print attendance["member"]["id"]

                obj, created = Attendance.objects.get_or_create(
                    attendance=True if str(attendance["status"]) == "attended" else False,
                    rsvp=rsvp,
                    event=event,
                    member=Member.objects.get(id=int(attendance["member"]["id"])),
                )

                if created:
                    count += 1

        modeladmin.message_user(request, "For event %s, received %d attendances. Saved %d attendances." %
                                (event.name, len(attendances), count))


def sync_rsvp(modeladmin, request, queryset):
    for event in queryset:
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

        modeladmin.message_user(request, "For event %s, received %d rsvps. Saved %d rsvps." %
                                (event.name, len(rsvps), count))


def team_coef(members):
    coefs = [member.win_lose_coefficient() for member in members]

    if len(coefs) > 0:
        return float(sum(coefs))/len(coefs)
    else:
        return 0.0


def generate_teams(event, no_of_iterations=30):
    coefficients = []
    teams_generated = []
    members = event.get_members_with_rsvp()

    # divide into two groups
    for i in range(no_of_iterations):
        random.shuffle(members)

        team_a = members[len(members)/2:]
        team_b = members[:len(members)/2]

        team_a_coef = team_coef(team_a)
        team_b_coef = team_coef(team_b)

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
        team_a, team_b = generate_teams(event, 100)

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
