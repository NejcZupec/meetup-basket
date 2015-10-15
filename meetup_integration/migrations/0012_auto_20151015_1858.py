# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0011_payment'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='payment',
            unique_together=set([('member', 'event')]),
        ),
    ]
