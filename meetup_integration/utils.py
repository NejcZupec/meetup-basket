import json
import requests

from django.conf import settings

from meetup_integration.models import Member, Group, Event, RSVP


class MeetupAPI():
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
            return r.json()["results"]
        except requests.exceptions.RequestException as e:
            print e


def sync_members(modeladmin, request, queryset):
    for group in queryset:
        members = MeetupAPI("2/members", group_id=group.id).get()

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
        events = MeetupAPI("2/events", group_id=group.id, status="past").get()

        for event in events:
            print json.dumps(event, indent=4)

            Event.objects.get_or_create(
                id=event["id"],
                name=event["name"],
                event_url=event["event_url"],
                group_id=Group.objects.get(id=event["group"]["id"]),
                status=event["status"],
            )

        modeladmin.message_user(request, "For group %s, received %d events." % (group.name, len(events)))


def sync_rsvps(modeladmin, request, queryset):
    for event in queryset:
        rsvps = MeetupAPI("2/rsvps", event_id=event.id).get()
        count = 0

        for rsvp in rsvps:
            print json.dumps(rsvp, indent=4)

            obj, created = RSVP.objects.get_or_create(
                id=rsvp["rsvp_id"],
                response=rsvp["response"],
                event_id=Event.objects.get(id=rsvp["event"]["id"]),
                member_id=Member.objects.get(id=rsvp["member"]["member_id"]),
            )

            if created:
                count += 1

        modeladmin.message_user(request, "For event %s, received %d rsvps. Saved %d rsvps." %
                                (event.name, len(rsvps), count))

