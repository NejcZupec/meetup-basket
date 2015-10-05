# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from meetup_integration.models import Event, Member, Coefficient


class Command(BaseCommand):
    help = "Calculate coefficients for each member."

    def handle(self, *args, **options):
        events = Event.objects.filter(status="past")

        for member in Member.objects.all():
            for i in range(len(events)):
                print events[:i+1]
                c = member.coefficient_for_events(events[:i+1])
                print str(member), events[i], c

                obj, created = Coefficient.objects.update_or_create(
                    member=member,
                    event=events[i],
                )

                obj.coefficient = c
                obj.save()

                if created:
                    print "Object has been added."
                else:
                    print "Object already exist. Values have been updated."

