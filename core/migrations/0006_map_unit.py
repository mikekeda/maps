# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-29 06:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170429_0515'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='unit',
            field=models.CharField(default='people / mi<sup>2</sup>', max_length=64),
            preserve_default=False,
        ),
    ]
