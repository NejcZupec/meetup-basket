# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from meetup_integration.models import Event, Member, Coefficient, Season

logger = logging.getLogger("meetup_basket")


class Command(BaseCommand):
    help = "Calculate coefficients for each member."

    def handle(self, *args, **options):

        for season in Season.objects.all():

            if season.slug == "all":
                events = Event.objects.filter(status="past")
            else:
                events = Event.objects.filter(status="past", season=season)

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
                        logger.info("Object has been added.")
                    else:
                        logger.info("Object already exist. Values have been updated.")
