import logging

from django.core.management.base import BaseCommand

from meetup_integration.models import Group
from meetup_integration.utils import sync_events

logger = logging.getLogger("meetup_basket")


class Command(BaseCommand):
    args = "group_urlname"
    help = "Get group by urlname."

    def handle(self, *args, **options):

        for group in Group.objects.all():
            message = sync_events(group)
            logger.info(message)
