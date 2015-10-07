# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0008_event_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='coefficient',
            name='season',
            field=models.ForeignKey(default=3, to='meetup_integration.Season'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='coefficient',
            unique_together=set([('member', 'event', 'season')]),
        ),
    ]
