# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0007_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='season',
            field=models.ForeignKey(default=1, to='meetup_integration.Season'),
            preserve_default=False,
        ),
    ]
