from django.conf import settings


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