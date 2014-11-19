# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0003_auto_20141119_2324'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attendance', models.BooleanField(default=True)),
                ('rsvp', models.CharField(max_length=255)),
                ('event', models.ForeignKey(to='meetup_integration.Event')),
                ('member', models.ForeignKey(to='meetup_integration.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
