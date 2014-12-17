from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django.views.decorators.cache import cache_page

from web.views import DashboardView, MembersView, MeetupsView, TeamGeneratorView, PaymentsView, clear_cache


urlpatterns = patterns('',
    url(r'^dashboard/$', cache_page(7*24*60*60)(DashboardView.as_view()), name='dashboard'),
    url(r'^$', cache_page(7*24*60*60)(MembersView.as_view()), name='members'),
    url(r'^meetups/$', cache_page(7*24*60*60)(MeetupsView.as_view()), name='meetups'),
    url(r'^payments/$', cache_page(7*24*60*60)(PaymentsView.as_view()), name='payments'),
    url(r'^team-generator/$', cache_page(7*24*60*60)(TeamGeneratorView.as_view()), name='team_generator'),

    url(r'clear-cache/$', clear_cache, name='clear_cache'),

    url(r'^admin/', include(admin.site.urls)),
)
