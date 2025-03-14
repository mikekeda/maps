# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-07 06:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20170507_0603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='date_of_information',
            field=models.DateField(blank=True, default=django.utils.timezone.now, help_text='An year or date when the information was measured.'),
        ),
    ]
