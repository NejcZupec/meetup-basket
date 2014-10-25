import operator

from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        members = Member.objects.all()

        payload = {'members': members}

        for member in members:
            print member.name, member.count_wins()

        return render(request, self.template_name, payload)


class MeetupsView(TemplateView):
    template_name = "meetups.html"

    def get(self, request):
        payload = {"events": []}

        event_objects = Event.objects.all().order_by("-name")

        for event in event_objects:
            payload["events"].append({
                "event": event,
                "teams": Team.objects.filter(event=event)
            })

        print payload

        return render(request, self.template_name, payload)
