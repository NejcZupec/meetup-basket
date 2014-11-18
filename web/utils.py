import random

from django.conf import settings


def team_coef(members):
    coefs = [member.win_lose_coefficient() for member in members]

    if len(coefs) > 0:
        return float(sum(coefs))/len(coefs)
    else:
        return 0.0


def generate_teams(members, no_of_iterations=30):
    coefficinents = []
    teams_generated = []

    # divide into two groups
    for i in range(no_of_iterations):
        random.shuffle(members)

        team_a = members[len(members)/2:]
        team_b = members[:len(members)/2]

        team_a_coef = team_coef(team_a)
        team_b_coef = team_coef(team_b)

        coef = abs(team_a_coef - team_b_coef)

        teams_generated.append((team_a, team_b))
        coefficinents.append(coef)

    index = coefficinents.index(min(coefficinents))

    team_a, team_b = teams_generated[index]

    # sort by coefficient
    team_a.sort(key=lambda member: member.win_lose_coefficient(), reverse=True)
    team_b.sort(key=lambda member: member.win_lose_coefficient(), reverse=True)

    return team_a, team_b


def calculate_weight(attended, rsvp):
    """
    Calculate a penalty weight for the attendee.

    :param attended: True or False
    :param rsvp: 'no' or 'yes'
    :return: A penalty weight.
    """

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
    return round(member.weight(event)/event.weight() * settings.MEETUP_PRICE, 2)


def generate_payments_table(members, events):
    table_rows = []

    for member in members:
        row = []
        for event in events:
            row.append({
                "attended": event.member_attended(member),
                "rsvp": event.get_member_rsvp(member),
                "weight": member.weight(event),
                "price": calculate_price(member, event),
            })

        row.append({
            "attended": None,
            "rsvp": None,
            "weight": None,
            "price": sum([r["price"] for r in row])
        })

        table_rows.append({"member": member.name, "data": row})



    return table_rows