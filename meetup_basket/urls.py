from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

from web.views import DashboardView, MembersView, MeetupsView, TeamGeneratorView, HallRentView, \
    coefficients_over_meetups_graph, TeamGeneratorExportView, TransactionsView, CostsView, cash_flow_graph


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^$', MembersView.as_view(), name='members'),
    url(r'^meetups/$', MeetupsView.as_view(), name='meetups'),
    url(r'^money/hall-rent/$', HallRentView.as_view(), name='hall-rent'),
    url(r'^money/transactions/$', TransactionsView.as_view(), name='transactions'),
    url(r'^money/costs/$', CostsView.as_view(), name='costs'),
    url(r'^team-generator/$', TeamGeneratorView.as_view(), name='team_generator'),
    url(r'^team-generator/export$', TeamGeneratorExportView.as_view(), name='team_generator_export'),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # AJAX
    url(r'coefficients_over_meetups_graph/$', coefficients_over_meetups_graph, name='coefficients_over_meetups_graph'),
    url(r'^money/cash-flow-graph/$', cash_flow_graph, name='cash_flow_graph'),
)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)