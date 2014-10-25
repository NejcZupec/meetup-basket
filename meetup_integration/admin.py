from django.contrib import admin

from meetup_integration.models import Group, Event, Member, RSVP
from meetup_integration.utils import MeetupAPI, sync_events, sync_members, sync_rsvps


class GroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "link", "url_name", "timezone"]
    actions = [sync_members, sync_events]


class MemberAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "link", "status"]


class EventAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "event_url", "group_id", "status"]
    actions = [sync_rsvps]


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Event, EventAdmin)