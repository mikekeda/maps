# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-25 10:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_remove_chart_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='description',
            field=models.TextField(blank=True, help_text='Chart description.', null=True),
        ),
    ]
