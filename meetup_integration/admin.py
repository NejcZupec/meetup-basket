from django.contrib import admin

from meetup_integration.models import Group


class GroupAdmin(admin.ModelAdmin):
    list_filter = ["name"]


admin.site.register(Group, GroupAdmin)