# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0002_rsvp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='event',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='member',
        ),
        migrations.DeleteModel(
            name='Attendance',
        ),
    ]
