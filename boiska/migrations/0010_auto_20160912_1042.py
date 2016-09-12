# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-12 08:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boiska', '0009_auto_20160912_0946'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('surname', models.CharField(max_length=40)),
                ('event_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_accepted', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='sportsground',
            name='end_season_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='sportsground',
            name='start_season_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='sports_ground',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='boiska.SportsGround'),
        ),
    ]
