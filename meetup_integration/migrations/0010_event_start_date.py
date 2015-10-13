# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0009_auto_20151007_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 13, 18, 51, 13, 332953, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
