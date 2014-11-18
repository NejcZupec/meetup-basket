# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RSVP',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('response', models.CharField(max_length=255)),
                ('event', models.ForeignKey(to='meetup_integration.Event')),
                ('member', models.ForeignKey(to='meetup_integration.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
