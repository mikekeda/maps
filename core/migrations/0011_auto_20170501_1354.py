# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 13:54
from __future__ import unicode_literals

import core.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20170501_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='base_color',
            field=core.models.ColorField(default='FFEDA0', max_length=6),
        ),
    ]