import logging

from django.conf import settings

from meetup_basket.utils import get_first_upcoming_event
from meetup_integration.models import Payment, Event, Team, Season, Member
from meetup_integration.utils import team_coef_weighted, team_diff_avg, team_weights

logger = logging.getLogger("meetup_basket")


def calculate_weight(attended, rsvp):
    """
    Calculate a penalty weight for the attendee.

    :param attended: True or False
    :param rsvp: 'no' or 'yes'
    :return: A penalty weight.
    """

    if rsvp == "waitlist":
        rsvp = "no"

    if attended and rsvp == "yes":
        return 1 + 0.0
    elif attended and not rsvp:
        return 1 + settings.PENALTY_WEIGHT
    elif attended and rsvp == "no":
        return 1 + 2*settings.PENALTY_WEIGHT
    elif not attended and rsvp == "no":
        return 0.0
    elif not attended and not rsvp:
        return settings.PENALTY_WEIGHT
    elif not attended and rsvp == "yes":
        return 2*settings.PENALTY_WEIGHT
    else:
        print "ERROR: this option is not implemented:", attended, rsvp


def calculate_price(member, event):
    try:
        return Payment.objects.get(member=member, event=event).price
    except Payment.DoesNotExist:
        return member.weight(event)/event.weight() * settings.MEETUP_PRICE


def generate_payments_table(members, events):
    table_rows = []

    for member in members:
        row = []
        for event in events:
            row.append({
                "price": calculate_price(member, event),
            })

        row.append({
            "price": sum([r["price"] for r in row])
        })

        table_rows.append({"member": member.name, "data": row})
    return table_rows


def prepare_payload_for_team_generator():
    try:
        next_event = get_first_upcoming_event()
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

        team_a_weights = team_weights(team_a, season)
        team_b_weights = team_weights(team_b, season)

        for i, member in enumerate(team_a):
            team_a_members.append({
                "name": member.name,
                "height": member.height,
                "games_played": member.games_played(season),
                "weight": team_a_weights[i],
                "count_wins": member.count_wins(season),
                "count_loses": member.count_loses(season),
                "win_lose_coefficient": member.win_lose_coefficient(season),
                "basket_diff": member.basket_diff(season),
                "basket_diff_avg": member.basket_diff_avg(season),
            })

        for i, member in enumerate(team_b):
            team_b_members.append({
                "name": member.name,
                "height": member.height,
                "games_played": member.games_played(season),
                "weight": team_b_weights[i],
                "count_wins": member.count_wins(season),
                "count_loses": member.count_loses(season),
                "win_lose_coefficient": member.win_lose_coefficient(season),
                "basket_diff": member.basket_diff(season),
                "basket_diff_avg": member.basket_diff_avg(season),
            })

        payload = {
            "event": event,
            "members": [],
            "teams": {
                "Team A": {
                    "members": team_a_members,
                    "height": sum([m["height"] for m in team_a_members])/(len(team_a_members)*1.0),
                    "coef": team_coef_weighted(team_a, season),
                    "diff": int(sum([m["basket_diff"] for m in team_a_members])),
                    "avg_diff": team_diff_avg(team_a, season),
                    "color": "bela majica",
                },
                "Team B": {
                    "members": team_b_members,
                    "height": sum([m["height"] for m in team_b_members])/(len(team_b_members)*1.0),
                    "coef": team_coef_weighted(team_b, season),
                    "diff": int(sum([m["basket_diff"] for m in team_b_members])),
                    "avg_diff": team_diff_avg(team_b, season),
                    "color": "barvna majica",
                }
            },
            "calculated": True,
            "next_event": next_event,
        }

        print payload
    except Exception, e:
        logger.warning("%s, %s" % (DeprecationWarning, e))

        payload = {
            "calculated": False,
            "next_event": next_event
        }

    return payload


def filter_members_by_attendance(attendance, season):
    """
    attendance = all, [0, 100] %
    season = [Season object]
    """
    events = Event.objects.filter(status="past") if season.slug == "all" else Event.objects.filter(status="past", season=season)
    count_all_events = events.count() * 1.0
    members = []

    for m in Member.objects.all():
        # filter members by attendance
        if attendance == "all" or m.meetups_attended(season) / count_all_events * 100.0 > attendance:
            members.append(m)

    return members
