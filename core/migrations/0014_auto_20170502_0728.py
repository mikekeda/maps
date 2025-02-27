# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 07:28
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20170502_0705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='opacity',
            field=models.DecimalField(decimal_places=2, default=0.7, help_text='The opacity for regions.', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
