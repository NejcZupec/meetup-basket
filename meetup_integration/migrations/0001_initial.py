# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('attendance', models.BooleanField(default=True)),
                ('rsvp', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('event_url', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('link', models.CharField(max_length=255)),
                ('url_name', models.CharField(max_length=255)),
                ('timezone', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('link', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255)),
                ('group', models.ForeignKey(to='meetup_integration.Group')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('match_win', models.IntegerField(default=0)),
                ('match_lose', models.IntegerField(default=0)),
                ('event', models.ForeignKey(to='meetup_integration.Event')),
                ('members', models.ManyToManyField(to='meetup_integration.Member')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(to='meetup_integration.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='event',
            field=models.ForeignKey(to='meetup_integration.Event'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attendance',
            name='member',
            field=models.ForeignKey(to='meetup_integration.Member'),
            preserve_default=True,
        ),
    ]
