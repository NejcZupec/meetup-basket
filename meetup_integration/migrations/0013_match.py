# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0012_auto_20151015_1858'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points_a', models.PositiveIntegerField(default=0.0)),
                ('points_b', models.PositiveIntegerField(default=0.0)),
                ('team_a', models.ForeignKey(related_name='team_a', to='meetup_integration.Team')),
                ('team_b', models.ForeignKey(related_name='team_b', to='meetup_integration.Team')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
