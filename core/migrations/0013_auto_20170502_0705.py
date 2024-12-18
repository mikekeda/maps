# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 07:05
from __future__ import unicode_literals

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20170501_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='opacity',
            field=models.DecimalField(decimal_places=2, default=0.7, help_text='The opacity for regions.', max_digits=5),
        ),
        migrations.AlterField(
            model_name='map',
            name='description',
            field=models.TextField(blank=True, help_text='Map description.', null=True),
        ),
        migrations.AlterField(
            model_name='map',
            name='end_color',
            field=core.models.ColorField(default='ffeda0', help_text='The color to fill regions with the lowest value.', max_length=6),
        ),
        migrations.AlterField(
            model_name='map',
            name='grades',
            field=models.PositiveSmallIntegerField(default=8, help_text='How many grades you would like to have'),
        ),
        migrations.AlterField(
            model_name='map',
            name='slug',
            field=models.SlugField(editable=False, help_text='The slug that will be user for urls.'),
        ),
        migrations.AlterField(
            model_name='map',
            name='start_color',
            field=core.models.ColorField(default='bd0026', help_text='The color to fill regions with the highest value.', max_length=6),
        ),
        migrations.AlterField(
            model_name='map',
            name='title',
            field=models.CharField(help_text='Map title.', max_length=256),
        ),
        migrations.AlterField(
            model_name='map',
            name='unit',
            field=models.CharField(help_text='The unit that will be used for the map.', max_length=64),
        ),
        migrations.AlterField(
            model_name='map',
            name='user',
            field=models.ForeignKey(help_text='Map owner.', on_delete=django.db.models.deletion.CASCADE, related_name='maps', to=settings.AUTH_USER_MODEL),
        ),
    ]
