import json

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team
from meetup_integration.utils import team_coef
from web.utils import generate_payments_table


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        members = sorted(Member.objects.all(), key=lambda member: member.win_lose_coefficient(), reverse=True)

        return render(request, self.template_name, {'members': members})


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


def coefficients_over_meetups_graph(request):
    events = Event.objects.filter(status="past")[4:]

    categories = [event.sequence_number() for event in events]
    series = []

    for member in Member.objects.all():
        data = [member.coefficient_after_event(events[i]) for i in range(len(events))]

        series.append({
            'name': member.name,
            'data': data,
        })

    payload = {
        "categories": categories,
        "series": series,
    }

    return HttpResponse(json.dumps(payload), content_type="application/json")


def clear_cache(request):
    cache.clear()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
