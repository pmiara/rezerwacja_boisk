# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-13 12:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boiska', '0010_auto_20160912_1042'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sportsground',
            unique_together=set([('name_prefix', 'local_id')]),
        ),
    ]