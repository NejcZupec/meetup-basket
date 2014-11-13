from django.core.management.base import BaseCommand

from meetup_integration.utils import MeetupAPI


class Command(BaseCommand):
    help = "Sync members with meetup."

    def handle(self, *args, **options):
        pass

