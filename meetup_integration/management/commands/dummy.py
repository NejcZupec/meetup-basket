from django.conf import settings
from django.core.management.base import BaseCommand

from meetup_integration.models import Member, Season


class Command(BaseCommand):
    args = "group_urlname"
    help = "Get group by urlname."

    def handle(self, *args, **options):

        season = Season.objects.get(name=settings.CURRENT_SEASON)

        for m in Member.objects.all():
            print m, m.basket_diff(season)




