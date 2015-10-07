from django.db import models


class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    url_name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)

    def __unicode__(self):
        return "Group <%s> (id=%s, url_name=%s)" % (self.name, self.id, self.url_name)


class Member(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    group = models.ForeignKey(Group)

    def meetups_attended(self):
        return Attendance.objects.filter(member=self, attendance=True).count()

    def count_wins(self):
        return sum([team.match_win for team in Team.objects.filter(members__id__exact=self.id)])

    def count_loses(self):
        return sum([team.match_lose for team in Team.objects.filter(members__id__exact=self.id)])

    def games_played(self):
        return self.count_wins() + self.count_loses()

    def win_lose_coefficient(self):
        if self.games_played() > 0:
            return float(self.count_wins())/self.games_played()
        else:
            return 0.5

    def weight(self, event):
        from web.utils import calculate_weight

        attended = event.member_attended(self)
        rsvp = event.get_member_rsvp(self)

        return float(calculate_weight(attended, rsvp))

    def coefficient_for_events(self, events):
        wins = 0.0
        loses = 0.0

        for event in events:
            for team in event.get_teams():
                if self in team.get_members():
                    wins += team.match_win
                    loses += team.match_lose

        if wins + loses > 0:
            return float(wins/(wins+loses))
        else:
            return 0.5

    def coefficient_after_event(self, event, season):
        try:
            return Coefficient.objects.get(event=event, member=self, season=season).coefficient
        except:
            return 0.0

    def __unicode__(self):
        return "Member <%s> (status=%s)" % (self.name, self.status)


class Event(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    event_url = models.CharField(max_length=255)
    group = models.ForeignKey(Group)
    status = models.CharField(max_length=255)
    season = models.ForeignKey("meetup_integration.Season")

    def get_members_with_rsvp(self, response="yes"):
        return [rsvp.member for rsvp in RSVP.objects.filter(event=self, response=response)]

    def member_attended(self, member):
        try:
            return Attendance.objects.get(event=self, member=member).attendance
        except Attendance.DoesNotExist:
            return False

    def weight(self):
        return sum([member.weight(self) for member in Member.objects.all()])

    def get_member_rsvp(self, member):
        try:
            return RSVP.objects.get(event=self, member=member).response
        except RSVP.DoesNotExist:
            return None

    def sequence_number(self):
        try:
            prefix = self.name.split(" ")[2]
            sn = prefix.split("#")[1]
        except Exception:
            print Exception
            sn = ""
        return sn

    def get_teams(self):
        return Team.objects.filter(event=self)

    def __unicode__(self):
        return "Event <%s> (status=%s)" % (self.name, self.status)


class Attendance(models.Model):
    attendance = models.BooleanField(default=True)
    rsvp = models.CharField(max_length=255)
    event = models.ForeignKey(Event)
    member = models.ForeignKey(Member)

    def __unicode__(self):
        return "Attendance for %s (attendance=%s, rsvp=%s, event=%s)" % (self.member.name,
                                                                         self.attendance,
                                                                         self.rsvp,
                                                                         self.event.name,)


class Team(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event)
    members = models.ManyToManyField(Member)
    match_win = models.IntegerField(default=0)
    match_lose = models.IntegerField(default=0)

    def get_members(self):
        return self.members.all()

    def __unicode__(self):
        return "Team <%s> (event=%s, match_win=%d, match_lose=%d)" % (self.name,
                                                                      self.event.name,
                                                                      self.match_win,
                                                                      self.match_lose,)


class RSVP(models.Model):
    id = models.IntegerField(primary_key=True)
    response = models.CharField(max_length=255)
    event = models.ForeignKey(Event)
    member = models.ForeignKey(Member)

    def __unicode__(self):
        return "RSVP <%s> (event=%d, member=%d)" % (self.response, self.event_id, self.member_id)


class Coefficient(models.Model):
    """
    Coefficient for each member after specific meetup (event).
    """
    member = models.ForeignKey(Member)
    event = models.ForeignKey(Event)
    coefficient = models.FloatField(default=0.5)
    season = models.ForeignKey("meetup_integration.Season")

    def __unicode__(self):
        return "Coefficient (member=%s, event=%s, coef=%f)" % (self.member, self.event, self.coefficient)

    class Meta:
        unique_together = ("member", "event", "season")


class Season(models.Model):
    """
    Each row represents a season.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __unicode__(self):
        return "Season (name=%s, slug=%s)" % (self.name, self.slug)
