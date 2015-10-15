# -*- coding: utf-8 -*-
import logging

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from meetup_integration.models import Event, Member, Coefficient, Season

logger = logging.getLogger("meetup_basket")


class Command(BaseCommand):
    help = "Calculate coefficients for each member. Steps: 1 - coefficients, 2 - payments."

    option_list = BaseCommand.option_list + (
        make_option("-s", "--steps", action="store", type="str", dest="steps",
                    help="List space delimited steps to be calculated."),
        make_option("-f", "--force", action="store_true", dest="force",
                    help="Flag for forcing the overwriting of existing entities. USE WITH CAUTION"),
        make_option("-a", "--all", action="store_true", dest="all", help="Calculate for all seasons."),
    )

    def handle(self, *args, **options):
        # steps
        try:
            steps = [int(o) for o in options["steps"].split()] if options["steps"] else None
        except Exception, e:
            logger.warning("Error with specified steps, will calculate all: %s" % str(e))
            steps = None

        # all seasons or only current
        if options["all"]:
            seasons = Season.objects.all()
        else:
            seasons = [Season.objects.get(name=settings.CURRENT_SEASON)]

        # STEP 1: calculate coefficients
        if steps is None or 1 in steps:
            logger.info("STEP 1: CALCULATING COEFFICIENTS")

            for season in seasons:
                logger.info("Calculating for season: %s" % season)

                if season.slug == "all":
                    events = Event.objects.filter(status="past").order_by("-start_date")
                else:
                    events = Event.objects.filter(status="past", season=season).order_by("-start_date")

                for member in Member.objects.all():
                    for i in range(len(events)):
                        logger.debug(events[:i+1])
                        c = member.coefficient_for_events(events[:i+1])

                        obj, created = Coefficient.objects.update_or_create(
                            member=member,
                            event=events[i],
                            season=season,
                        )

                        obj.coefficient = c
                        obj.save()

                        if created:
                            logger.info("Object (name=%s, event=%s) has been added." % (obj.member.name, obj.event.name))
                        else:
                            logger.info("Object (name=%s, event=%s) already exists. Values have been updated." %
                                        (obj.member.name, obj.event.name))
