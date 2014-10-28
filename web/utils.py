import random


def team_coef(members):
    coefs = [member.win_lose_coefficient() for member in members]

    if len(coefs) > 0:
        return float(sum(coefs))/len(coefs)
    else:
        return 0.0


def generate_teams(members, no_of_iterations=30):
    print len(members)

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

    print team_a

    return team_a, team_b
