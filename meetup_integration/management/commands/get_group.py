import json

from django.core.management.base import BaseCommand

from meetup_integration.models import Group
from meetup_integration.utils import MeetupAPI


class Command(BaseCommand):
    args = ""
    help = "Get group (first argument is group_id)."

    def handle(self, *args, **options):
        try:
            group_id = args[0]

            group_json = MeetupAPI("2/groups", group_id=group_id).get()["results"][0]

            print json.dumps(group_json, indent=4)

            Group.objects.get_or_create(
                id=group_json["id"],
                name=group_json["name"],
                link=group_json["link"],
                url_name=group_json["urlname"],
                timezone=group_json["timezone"],
            )

        except IndexError:
            print self.help

