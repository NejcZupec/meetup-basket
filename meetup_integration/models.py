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
            return None

    def __unicode__(self):
        return "Member <%s> (status=%s)" % (self.name, self.status)


class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    event_url = models.CharField(max_length=255)
    group = models.ForeignKey(Group)
    status = models.CharField(max_length=255)

    def get_members_with_rsvp(self, rsvp="yes"):
        return [a.member for a in Attendance.objects.filter(event=self, rsvp=rsvp)]

    def __unicode__(self):
        return "Event <%s> (status=%s)" % (self.name, self.status)


class Attendance(models.Model):
    id = models.IntegerField(primary_key=True)
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

