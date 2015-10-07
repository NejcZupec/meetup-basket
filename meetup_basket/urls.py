from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin

from django.views.decorators.cache import cache_page

from web.views import DashboardView, MembersView, MeetupsView, TeamGeneratorView, PaymentsView, clear_cache,\
    coefficients_over_meetups_graph


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^$', MembersView.as_view(), name='members'),
    url(r'^meetups/$', MeetupsView.as_view(), name='meetups'),
    url(r'^payments/$', cache_page(7*24*60*60)(PaymentsView.as_view()), name='payments'),
    url(r'^team-generator/$', TeamGeneratorView.as_view(), name='team_generator'),

    url(r'clear-cache/$', clear_cache, name='clear_cache'),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # AJAX
    url(r'coefficients_over_meetups_graph/$', cache_page(7*24*60*60)(coefficients_over_meetups_graph),
        name='coefficients_over_meetups_graph'),
)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)