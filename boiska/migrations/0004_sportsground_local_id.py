# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-11 18:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boiska', '0003_sportsground'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportsground',
            name='local_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]