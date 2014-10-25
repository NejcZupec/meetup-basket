from django.contrib import admin

from meetup_integration.models import Group, Event, Member, Attendance, Team
from meetup_integration.utils import sync_events, sync_members, sync_attendance


class GroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "link", "url_name", "timezone"]
    actions = [sync_members, sync_events]


class MemberAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "link", "status"]


class EventAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "event_url", "group", "status"]
    actions = [sync_attendance]


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "attendance", "rsvp", "event", "member"]


class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "event", "match_win", "match_lose"]


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Team, TeamAdmin)