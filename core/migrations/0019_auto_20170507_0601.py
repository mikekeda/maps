# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-07 06:01
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_map_date_of_information'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='date_of_information',
            field=models.DateField(blank=True, default=datetime.datetime(2017, 5, 7, 6, 1, 20, 759858), help_text='An year or date when the information was measured.'),
        ),
        migrations.AlterField(
            model_name='map',
            name='unit',
            field=models.CharField(blank=True, help_text='The unit that will be used for the map.', max_length=64),
        ),
    ]
