import json
import requests

from django.conf import settings

from meetup_integration.models import Member, Group, Event, Attendance, RSVP


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
            print url
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


def sync_events(modeladmin, request, queryset):
    for group in queryset:
        events = MeetupAPI("2/events", group_id=group.id).get()["results"]

        for event in events:
            print json.dumps(event, indent=4)

            Event.objects.get_or_create(
                id=event["id"],
                name=event["name"],
                event_url=event["event_url"],
                group=Group.objects.get(id=event["group"]["id"]),
                status=event["status"],
            )

        modeladmin.message_user(request, "For group %s, received %d events." % (group.name, len(events)))


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
