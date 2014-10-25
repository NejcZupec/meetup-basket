from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from web.views import DashboardView, MembersView


urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    url(r'^members/$', MembersView.as_view(), name='members'),

    url(r'^admin/', include(admin.site.urls)),
)
