# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0004_attendance'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coefficient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coefficient', models.FloatField()),
                ('event', models.ForeignKey(to='meetup_integration.Event')),
                ('member', models.ForeignKey(to='meetup_integration.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='coefficient',
            unique_together=set([('member', 'event')]),
        ),
    ]
