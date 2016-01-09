# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meetup_integration', '0015_member_height'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(help_text=b'When a transaction has been executed.')),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('amount', models.FloatField()),
                ('type', models.CharField(max_length=20, choices=[(b'membership_fee', b'Membership Fee'), (b'meetup_fee', b'Meetup Fee'), (b'hall_rent', b'Hall Rent')])),
                ('member', models.ForeignKey(blank=True, to='meetup_integration.Member', null=True)),
                ('season', models.ForeignKey(to='meetup_integration.Season')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
