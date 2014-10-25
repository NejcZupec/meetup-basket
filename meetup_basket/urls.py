from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from dashboard.views import DashboardView

urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
