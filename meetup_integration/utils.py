import requests

from django.conf import settings


class MeetupAPI():
    def __init__(self, func, **kwargs):
        self.func = func
        self.kwargs = kwargs

    def generate_url(self):
        arg_string = "?"
        for key, value in self.kwargs.items():
            arg_string += ("&" + str(key) + "=" + str(value))
        return settings.MEETUP_API_URL + self.func + arg_string + "&key=" + settings.MEETUP_API_KEY

    def get(self):
        try:
            r = requests.get(self.generate_url())
            return r.json()
        except requests.exceptions.RequestException as e:
            print e
