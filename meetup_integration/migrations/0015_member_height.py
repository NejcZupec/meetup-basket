# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0014_auto_20151019_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='height',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
