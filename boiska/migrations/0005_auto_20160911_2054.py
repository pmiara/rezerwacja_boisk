# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-11 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boiska', '0004_sportsground_local_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sportsground',
            name='local_id',
            field=models.PositiveIntegerField(blank=True),
        ),
    ]
