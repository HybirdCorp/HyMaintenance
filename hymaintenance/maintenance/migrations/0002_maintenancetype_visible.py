# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-20 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancetype',
            name='visible',
            field=models.BooleanField(default=False, verbose_name='Visible to simple user'),
        ),
    ]
