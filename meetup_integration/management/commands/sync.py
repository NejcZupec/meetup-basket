import logging

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from meetup_integration.models import Group, Event, Season
from meetup_integration.utils import sync_events, sync_attendance, sync_rsvp

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

        current_season = Season.objects.get(name=settings.CURRENT_SEASON)

        # STEP 1: sync events
        if steps is None or 1 in steps:
            logger.info("SYNC EVENTS")

            for group in Group.objects.all():
                logger.info("Syncing events for group: %s" % group.name)
                message = sync_events(group)
                logger.info(message)

        # STEP 2: sync RSVPS
        if steps is None or 2 in steps:
            logger.info("SYNC RSVPS")

            for event in Event.objects.filter(season=current_season):
                logger.info("Syncing RSVPs for event: %s" % event.name)
                message = sync_rsvp(event)
                logger.info(message)

        # STEP 3: sync attendance
        if steps is None or 3 in steps:
            logger.info("SYNC ATTENDANCE")

            for event in Event.objects.filter(season=current_season):
                logger.info("Syncing attendance for event: %s" % event.name)
                message = sync_attendance(event)
                logger.info(message)


