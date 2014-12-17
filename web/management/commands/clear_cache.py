from django.core.cache import cache
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        print "Cache has been cleared."