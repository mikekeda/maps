# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 10:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20170502_0728'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='changed',
            field=models.DateTimeField(auto_now=True, help_text='Time when map was changed last time.'),
        ),
    ]
