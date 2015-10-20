from django.core.management.base import BaseCommand

from meetup_integration.models import Event
from meetup_integration.utils import generate_teams_for_event


class Command(BaseCommand):
    args = "group_urlname"
    help = "Get group by urlname."

    def handle(self, *args, **options):
        next_event = Event.objects.filter(status="upcoming").earliest("start_date")
        generate_teams_for_event(next_event)
