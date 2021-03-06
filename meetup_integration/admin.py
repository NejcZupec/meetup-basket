from django.contrib import admin

from meetup_integration.models import Group, Event, Member, Attendance, Team, RSVP, Coefficient, Season, Match, \
    Payment, Transaction
from meetup_integration.utils import sync_events_queryset, sync_members, sync_attendance_queryset, sync_rsvp_queryset, \
    generate_teams_admin


class GroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "link", "url_name", "timezone"]
    actions = [sync_members, sync_events_queryset]


class MemberAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "link", "status", "height"]


class EventAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "event_url", "start_date", "status", "season"]
    actions = [sync_attendance_queryset, sync_rsvp_queryset, generate_teams_admin]
    list_filter = ["season", "status"]


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "attendance", "rsvp", "event", "member"]
    list_filter = ["event"]


class TeamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "event", "match_win", "match_lose"]


class RSVPAdmin(admin.ModelAdmin):
    list_display = ["id", "response", "event", "member"]
    list_filter = ["event__season", "event"]
    search_fields = ["id"]


class CoefficientAdmin(admin.ModelAdmin):
    list_display = ["id", "member", "event", "coefficient", "basket_diff", "season"]
    list_filter = ["member", "event", "season"]


class SeasonAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug"]


class MatchAdmin(admin.ModelAdmin):
    list_display = ["id", "team_a", "team_b", "points_a", "points_b"]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "member", "event", "price"]
    list_filter = ["member", "event"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "date", "description", "amount", "member", "type"]
    list_filter = ["member", "type", "date"]


admin.site.register(Group, GroupAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(RSVP, RSVPAdmin)
admin.site.register(Coefficient, CoefficientAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Transaction, TransactionAdmin)
