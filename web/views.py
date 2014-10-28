import random

from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event, Team


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        members = Member.objects.all()

        payload = {'members': members}

        for member in members:
            print member.name, member.count_wins()

        return render(request, self.template_name, payload)


class MeetupsView(TemplateView):
    template_name = "meetups.html"

    def get(self, request):
        payload = {"events": []}

        event_objects = Event.objects.all().order_by("-name")

        for event in event_objects:
            payload["events"].append({
                "event": event,
                "teams": Team.objects.filter(event=event)
            })

        return render(request, self.template_name, payload)


class TeamGeneratorView(TemplateView):
    template_name = "team_generator.html"

    def get(self, request):
        payload = {}

        # generate teams
        event = Event.objects.latest("name")

        payload["event"] = event

        members = event.get_members_with_rsvp()

        print len(members)

        coefficinents = []
        teams_generated = []

        def team_coef(members):
            coefs = [member.win_lose_coefficient() for member in members]

            if len(coefs) > 0:
                return float(sum(coefs))/len(coefs)
            else:
                return 0.0

        # divide into two groups
        for i in range(50):
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

        payload["team_a_c"] = team_coef(team_a)
        payload["team_b_c"] = team_coef(team_b)

        payload["teams"] = {
            "A": team_a,
            "B": team_b,
        }

        payload["members"] = members

        return render(request, self.template_name, payload)


class PaymentsView(TemplateView):
    template_name = "payments.html"