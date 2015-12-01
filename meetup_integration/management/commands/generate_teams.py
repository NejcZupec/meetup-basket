from optparse import make_option

from django.core.management.base import BaseCommand

from meetup_integration.models import Event
from meetup_integration.utils import generate_teams_for_event


class Command(BaseCommand):
    help = "Generate teams."
    option_list = BaseCommand.option_list + (
        make_option("-s", "--selection", action="store", type="int", dest="selection",
                    help="Select a combination [0-n]."),
    )

    def handle(self, *args, **options):
        next_event = Event.objects.filter(status="upcoming").earliest("start_date")

        selection = options.get("selection", None)

        generate_teams_for_event(next_event, selection=selection)
