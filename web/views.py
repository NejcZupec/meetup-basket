import json

from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team, Season
from meetup_integration.utils import team_coef
from web.utils import generate_payments_table


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        season_id = request.GET.get("season_id")
        members = []
        season = Season.objects.get(pk=season_id) if season_id else Season.objects.get(name=settings.CURRENT_SEASON)

        for m in Member.objects.all():
            members.append({
                "name": m.name,
                "meetups_attended": m.meetups_attended(season),
                "games_played": m.games_played(season),
                "count_wins": m.count_wins(season),
                "count_loses": m.count_loses(season),
                "win_lose_coefficient": m.win_lose_coefficient(season),
            })

        return render(request, self.template_name, {
            'members': members,
            'season': season,
            'seasons': Season.objects.all()
        })


class MeetupsView(TemplateView):
    template_name = "meetups.html"

    def get(self, request):
        payload = {"events": []}

        event_objects = Event.objects.filter(start_date__lte=datetime.utcnow()).order_by("-start_date")

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

        season = Season.objects.get(name=settings.CURRENT_SEASON)

        payload = {
            "event": event,
            "members": [],
            "teams": {
                "Team A": {
                    "members": team_a,
                    "coef": team_coef(team_a, season),
                },
                "Team B": {
                    "members": team_b,
                    "coef": team_coef(team_b, season),
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
    """
    GET parameters:
    - season_id
    """
    season_id = request.GET.get("season_id")

    if season_id:
        season = Season.objects.get(pk=season_id)
    else:
        season = Season.objects.get(name=settings.CURRENT_SEASON)

    if season.slug == "all":
        events = Event.objects.filter(status="past")
    else:
        events = Event.objects.filter(status="past", season=season)

    categories = [event.sequence_number() for event in events]
    series = []

    for member in Member.objects.all():
        data = [member.coefficient_after_event(events[i], season) for i in range(len(events))]

        series.append({
            'name': member.name,
            'data': data,
        })

    payload = {
        "categories": categories,
        "series": series,
    }

    return HttpResponse(json.dumps(payload), content_type="application/json")
