import random

from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team
from web.utils import team_coef, generate_teams


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

        return render(request, self.template_name, payload)


class TeamGeneratorView(TemplateView):
    template_name = "team_generator.html"

    def get(self, request):
        # get the latest event
        event = Event.objects.latest("name")

        # members
        members = event.get_members_with_rsvp()
        team_a, team_b = generate_teams(members)

        payload = {
            "event": event,
            "members": members,
            "teams": {
                "Team A": {
                    "members": team_a,
                    "coef": team_coef(team_a),
                },
                "Team B": {
                    "members": team_b,
                    "coef": team_coef(team_b)
                }
            }
        }

        return render(request, self.template_name, payload)


class PaymentsView(TemplateView):
    template_name = "payments.html"