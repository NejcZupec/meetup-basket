import calendar
import json
import logging

from datetime import datetime

from django.conf import settings
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team, Season, Transaction
from web.utils import generate_payments_table, prepare_payload_for_team_generator, filter_members_by_attendance

logger = logging.getLogger("meetup_basket")


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        """
        GET parameters:
        - season_id
        - attendance: interval 0...100 % or [all] == show all players
        """
        season_id = request.GET.get("season_id", Season.objects.get(name=settings.CURRENT_SEASON).pk)
        attendance = request.GET.get("attendance", 50)
        attendance = int(attendance) if attendance != "all" else attendance
        season = Season.objects.get(pk=season_id)
        members = []

        for m in filter_members_by_attendance(attendance, season):
            members.append({
                "name": m.name,
                "height": m.height,
                "meetups_attended": m.meetups_attended(season),
                "games_played": m.games_played(season),
                "count_wins": m.count_wins(season),
                "count_loses": m.count_loses(season),
                "win_lose_coefficient": m.win_lose_coefficient(season),
                "basket_diff": int(m.basket_diff(season)),
                "basket_diff_avg": m.basket_diff_avg(season),
            })

        return render(request, self.template_name, {
            'members': members,
            'season': season,
            'seasons': Season.objects.all(),
            'attendance': attendance,
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
        payload = prepare_payload_for_team_generator()
        return render(request, self.template_name, payload)


class TeamGeneratorExportView(TemplateView):
    template_name = "team_generator_export.html"

    def get(self, request, *args, **kwargs):
        payload = prepare_payload_for_team_generator()
        return render(request, self.template_name, payload, content_type='text/plain; charset=utf-8')


class HallRentView(TemplateView):
    template_name = "hall_rent.html"

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


class TransactionsView(TemplateView):
    template_name = "transactions.html"

    def get(self, request):
        season_id = request.GET.get("season_id")
        season = Season.objects.get(pk=season_id) if season_id else Season.objects.get(name=settings.CURRENT_SEASON)

        payload = {
            "seasons": Season.objects.filter(~Q(slug="all")),
            "season": season,
            "transactions": Transaction.objects.filter(season=season),
            "balance": Transaction.objects.filter(season=season).aggregate(balance=Sum("amount")).get("balance", 0.0),
            "hall_rent": Transaction.objects.filter(season=season, type="hall_rent").aggregate(hall_rent=Sum("amount")).get("hall_rent", 0.0),
            "meetup_fee": Transaction.objects.filter(season=season, type="meetup_fee").aggregate(meetup_fee=Sum("amount")).get("meetup_fee", 0.0),
            "membership_fee": Transaction.objects.filter(season=season, type="membership_fee").aggregate(membership_fee=Sum("amount")).get("membership_fee", 0.0),
        }

        return render(request, self.template_name, payload)


class CostsView(TemplateView):
    template_name = "costs.html"

    def get(self, request):
        season_id = request.GET.get("season_id")
        season = Season.objects.get(pk=season_id) if season_id else Season.objects.get(name=settings.CURRENT_SEASON)
        members = []

        for m in Member.objects.all():
            members.append({
                "name": m.name,
                "meetup_fee": m.meetup_fee_for_season(season),
                "hall_rent": m.hall_rent_for_season(season),
                "costs": m.costs_for_season(season),
                "contribution": m.contribution_for_season(season),
                "balance": m.balance_for_season(season),
            })

        payload = {
            "seasons": Season.objects.filter(~Q(slug="all")),
            "season": season,
            "members": members,
        }

        return render(request, self.template_name, payload)


def coefficients_over_meetups_graph(request):
    """
    GET parameters:
    - season_id
    """
    season_id = request.GET.get("season_id")
    attendance = request.GET.get("attendance", 50)
    attendance = int(attendance) if attendance != "all" else attendance

    season = Season.objects.get(pk=season_id) if season_id else Season.objects.get(name=settings.CURRENT_SEASON)
    events = Event.objects.filter(status="past").order_by("start_date") if season.slug == "all" else \
        Event.objects.filter(status="past", season=season).order_by("start_date")

    categories = [event.sequence_number() for event in events]
    series = []

    for member in filter_members_by_attendance(attendance, season):
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


def cash_flow_graph(request):
    """
    GET parameters
    - season_id
    """
    season_id = request.GET.get("season_id")
    season = Season.objects.get(pk=season_id) if season_id else Season.objects.get(name=settings.CURRENT_SEASON)

    data = []
    transactions = Transaction.objects.filter(season=season).order_by("date")
    cash_flow = [t.amount for t in transactions]

    for i, t in enumerate(transactions):
        data.append([calendar.timegm(t.date.timetuple())*1000, sum(cash_flow[:i+1])])

    return HttpResponse(json.dumps(data), content_type="application/json")
