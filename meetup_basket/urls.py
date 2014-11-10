from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from web.views import DashboardView, MembersView, MeetupsView, TeamGeneratorView, PaymentsView


urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    url(r'^meetups/$', MeetupsView.as_view(), name='meetups'),
    url(r'^members/$', MembersView.as_view(), name='members'),
    url(r'^team-generator/$', TeamGeneratorView.as_view(), name='team_generator'),
    url(r'^payments/$', PaymentsView.as_view(), name='payments'),

    url(r'^admin/', include(admin.site.urls)),
)
