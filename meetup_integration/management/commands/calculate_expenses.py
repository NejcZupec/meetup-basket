import collections
import datetime
import logging
import time

from django.core.management.base import BaseCommand

from meetup_integration.utils import MeetupAPI

logger = logging.getLogger("meetup_basket")

GROUP_ID = 16919132


class Command(BaseCommand):

    def handle(self, *args, **options):
        visits_per_member_id = collections.defaultdict(int)

        # 1) get members
        members_api = MeetupAPI("2/members", group_id=GROUP_ID).get()
        members = members_api["results"]
        members_dict = {member["id"]: member["name"] for member in members}

        # 2) get events
        events_api = MeetupAPI("2/events", group_id=GROUP_ID, status="past").get()
        events = events_api["results"]
        start_season_date = datetime.datetime(year=2016, month=7, day=30)
        filtered_events = [event for event in events if datetime.datetime.fromtimestamp(event["time"] / 1000) > start_season_date]
        event_ids = [event["id"] for event in filtered_events]

        # 3) get RSVPs
        for event_id in event_ids:
            rsvps = MeetupAPI("2/rsvps", event_id=event_id, rsvp="yes").get()

            try:
                print event_id, len(rsvps["results"])
                for rsvp in rsvps["results"]:
                    member_id = rsvp["member"]["member_id"]
                    visits_per_member_id[member_id] += 1

            except Exception:
                print "Results haven't been returned."

            time.sleep(1)

        # 4) print price per member name
        for member_id in members_dict:
            print members_dict[member_id], visits_per_member_id[member_id]
