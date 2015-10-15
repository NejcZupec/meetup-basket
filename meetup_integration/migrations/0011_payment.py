# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0010_event_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.FloatField(default=0.0)),
                ('event', models.ForeignKey(to='meetup_integration.Event')),
                ('member', models.ForeignKey(to='meetup_integration.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
