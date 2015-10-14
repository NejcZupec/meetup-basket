# -*- coding: utf-8 -*-
import logging

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from meetup_integration.models import Event, Member, Coefficient, Season

logger = logging.getLogger("meetup_basket")


class Command(BaseCommand):
    help = "Calculate coefficients for each member."
    option_list = BaseCommand.option_list + (
        make_option("-f", "--force", action="store_true", dest="force",
                    help="Flag for forcing the overwriting of existing entities. USE WITH CAUTION"),
    )

    def handle(self, *args, **options):

        if options["force"]:
            seasons = Season.objects.all()
        else:
            seasons = [Season.objects.get(name=settings.CURRENT_SEASON)]

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
