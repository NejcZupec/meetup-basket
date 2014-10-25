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
    group_id = models.ForeignKey(Group)
    status = models.CharField(max_length=255)

    def __unicode__(self):
        return "Event <%s> (status=%s)" % (self.name, self.status)


class RSVP(models.Model):
    id = models.IntegerField(primary_key=True)
    response = models.CharField(max_length=255)
    event_id = models.ForeignKey(Event)
    member_id = models.ForeignKey(Member)

    def __unicode__(self):
        return "RSVP <%s> (event=%d, member=%d)" % (self.response, self.event_id, self.member_id)
