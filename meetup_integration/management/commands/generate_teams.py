from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

from meetup_integration.models import Event
from meetup_integration.utils import generate_teams_for_event


class Command(BaseCommand):
    help = "Generate teams."
    option_list = BaseCommand.option_list + (
        make_option("-c", "--combination", action="store", type="int", dest="combination",
                    help="Select a combination [0-n]."),
        make_option("-s", "--sync", action="store_true", dest="sync", help="Force RSVP sync."),
    )

    def handle(self, *args, **options):
        if options.get("sync"):
            call_command("sync", force=True, step=2)

        next_event = Event.objects.filter(start_date__gte=timezone.now()).earliest("start_date")
        combination = options.get("combination", None)
        generate_teams_for_event(next_event, combination=combination)
