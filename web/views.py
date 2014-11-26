from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team
from meetup_integration.utils import team_coef


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        members = Member.objects.all()

        members = sorted(members, key=lambda member: member.win_lose_coefficient(), reverse=True)

        payload = {'members': members}

        return render(request, self.template_name, payload)


class MeetupsView(TemplateView):
    template_name = "meetups.html"

    def get(self, request):
        payload = {"events": []}

        event_objects = Event.objects.all().order_by("-id")

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
        event = Event.objects.latest("id")

        team_a = Team.objects.get(name="A", event=event).members.all()
        team_b = Team.objects.get(name="B", event=event).members.all()


        payload = {
            "event": event,
            "members": [],
            "teams": {
                "Team A": {
                    "members": team_a,
                    "coef": team_coef(team_a),
                },
                "Team B": {
                    "members": team_b,
                    "coef": team_coef(team_b),
                }
            }
        }

        return render(request, self.template_name, payload)


class PaymentsView(TemplateView):
    template_name = "payments.html"

    def get(self, request):
        members = Member.objects.all()
        events = Event.objects.filter(status="past")

        payload = {
            "members": members,
            "events": events,
            "payments_table": generate_payments_table(members, events),
        }

        return render(request, self.template_name, payload)
