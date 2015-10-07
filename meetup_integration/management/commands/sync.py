import logging

from optparse import make_option

from django.core.management.base import BaseCommand

from meetup_integration.models import Group, Event
from meetup_integration.utils import sync_events, sync_attendance

logger = logging.getLogger("meetup_basket")


class Command(BaseCommand):
    help = "Sync members with meetup."

    option_list = BaseCommand.option_list + (
        make_option("-s", "--steps", action="store", type="str", dest="steps",
                    help="List space delimited steps to be calculated."),
    )

    def handle(self, *args, **options):

        try:
            steps = [int(o) for o in options["steps"].split()] if options["steps"] else None
        except Exception, e:
            logger.warning("Error with specified steps, will calculate all: %s" % str(e))
            steps = None

        # STEP 1: sync events
        if 1 in steps or steps is None:
            logger.info("SYNC EVENTS")

            for group in Group.objects.all():
                message = sync_events(group)
                logger.info(message)

        # STEP 2: sync attendance
        if 2 in steps or steps is None:
            logger.info("SYNC ATTENDANCE")

            for event in Event.objects.all():
                logger.info("Syncing attendance for event: %s" % event.name)
                sync_attendance(event)


