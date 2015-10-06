# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0005_auto_20151005_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coefficient',
            name='coefficient',
            field=models.FloatField(default=0.5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='id',
            field=models.CharField(max_length=255, serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
