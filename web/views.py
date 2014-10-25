from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member, Event


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        payload = {'members': Member.objects.all()}

        return render(request, self.template_name, payload)


class MeetupsView(TemplateView):
    template_name = "meetups.html"

    def get(self, request):
        payload = {
            'events': Event.objects.all().order_by("-name")
        }



        return render(request, self.template_name, payload)
