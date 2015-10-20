import json
import logging

from datetime import datetime

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team, Season
from meetup_integration.utils import team_coef
from web.utils import generate_payments_table

logger = logging.getLogger("meetup_basket")


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
                "basket_diff": int(m.basket_diff(season)),
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
        try:
            next_event = Event.objects.filter(status="upcoming").earliest("start_date")
        except Event.DoesNotExist:
            logger.error("Upcoming events don't exist. Sync them with meetup.")
            next_event = ""

        try:
            # get the latest event
            event = next_event

            team_a = Team.objects.get(name="A", event=event).members.all()
            team_b = Team.objects.get(name="B", event=event).members.all()

            season = Season.objects.get(name=settings.CURRENT_SEASON)

            team_a_members = []
            team_b_members = []

            for member in team_a:
                team_a_members.append({
                    "name": member.name,
                    "games_played": member.games_played(season),
                    "count_wins": member.count_wins(season),
                    "count_loses": member.count_loses(season),
                    "win_lose_coefficient": member.win_lose_coefficient(season),
                    "basket_diff": member.basket_diff(season),
                })

            for member in team_b:
                team_b_members.append({
                    "name": member.name,
                    "games_played": member.games_played(season),
                    "count_wins": member.count_wins(season),
                    "count_loses": member.count_loses(season),
                    "win_lose_coefficient": member.win_lose_coefficient(season),
                    "basket_diff": member.basket_diff(season),
                })


            payload = {
                "event": event,
                "members": [],
                "teams": {
                    "Team A": {
                        "members": team_a_members,
                        "coef": team_coef(team_a, season),
                        "diff": sum([m["basket_diff"] for m in team_a_members]),
                    },
                    "Team B": {
                        "members": team_b_members,
                        "coef": team_coef(team_b, season),
                        "diff": sum([m["basket_diff"] for m in team_b_members]),
                    }
                },
                "calculated": True,
                "next_event": next_event,
            }
        except Exception, e:
            logger.warning("%s, %s" % (DeprecationWarning, e))

            payload = {
                "calculated": False,
                "next_event": next_event
            }

        return render(request, self.template_name, payload)


class PaymentsView(TemplateView):
    template_name = "payments.html"

    def get(self, request):
        season_id = request.GET.get("season_id")
        members = Member.objects.all()
        season = Season.objects.get(pk=season_id) if season_id else Season.objects.get(name=settings.CURRENT_SEASON)
        events = Event.objects.filter(status="past", season=season).order_by("start_date")

        payload = {
            "members": members,
            "events": events,
            "payments_table": generate_payments_table(members, events),
            "seasons": Season.objects.filter(~Q(slug="all")),
            "season": season,
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
        events = Event.objects.filter(status="past").order_by("start_date")
    else:
        events = Event.objects.filter(status="past", season=season).order_by("start_date")

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
