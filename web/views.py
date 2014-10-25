from django.shortcuts import render
from django.views.generic import TemplateView

from meetup_integration.models import Member


class DashboardView(TemplateView):
    template_name = "dashboard.html"


class MembersView(TemplateView):
    template_name = "members.html"

    def get(self, request):
        payload = {'members': Member.objects.all()}

        return render(request, self.template_name, payload)
