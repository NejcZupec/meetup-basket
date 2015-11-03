import logging

from django.conf import settings

from meetup_integration.models import Payment, Event, Team, Season
from meetup_integration.utils import team_coef

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
        return round(member.weight(event)/event.weight() * settings.MEETUP_PRICE, 2)


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

        team_a_diff = int(sum([m["basket_diff"] for m in team_a_members]))
        team_b_diff = int(sum([m["basket_diff"] for m in team_b_members]))

        payload = {
            "event": event,
            "members": [],
            "teams": {
                "Team A": {
                    "members": team_a_members,
                    "coef": team_coef(team_a, season),
                    "diff": "+%d" % team_a_diff if team_a_diff > 0 else team_a_diff,
                    "color": "bela majica"
                },
                "Team B": {
                    "members": team_b_members,
                    "coef": team_coef(team_b, season),
                    "diff": "+%d" % team_b_diff if team_a_diff > 0 else team_b_diff,
                    "color": "barvna majica"
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

    return payload
