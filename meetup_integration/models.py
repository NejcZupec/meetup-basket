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

    def __unicode__(self):
        return "Member <%s> (status=%s)" % (self.name, self.status)


class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    event_url = models.CharField(max_length=255)
    group = models.ForeignKey(Group)
    status = models.CharField(max_length=255)

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

    def __unicode__(self):
        return "Team <%s> (event=%s, match_win=%d, match_lose=%d)" % (self.name,
                                                                      self.event.name,
                                                                      self.match_win,
                                                                      self.match_lose,)

