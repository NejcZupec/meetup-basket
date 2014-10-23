from django.db import models


class Group(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    url_name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)

    def __unicode__(self):
        return "Group %s (id=%s, url_name=%s)" % (self.name, self.id, self.url_name)
