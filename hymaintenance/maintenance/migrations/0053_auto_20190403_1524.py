# Generated by Django 2.0.13 on 2019-04-03 13:24

import django.utils.timezone
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0052_auto_20190328_1132")]

    operations = [
        migrations.AddField(
            model_name="maintenancecontract",
            name="recurrence_last_date",
            field=models.DateField(blank=True, null=True, verbose_name="Last recurrence date"),
        ),
        migrations.AddField(
            model_name="maintenancecontract",
            name="recurrence_next_date",
            field=models.DateField(blank=True, null=True, verbose_name="Next recurrence date"),
        ),
        migrations.AlterField(
            model_name="maintenancecontract",
            name="reset_date",
            field=models.DateField(blank=True, null=True, verbose_name="Last reset date"),
        ),
        migrations.AlterField(
            model_name="maintenancecontract",
            name="start",
            field=models.DateField(default=django.utils.timezone.now, verbose_name="Start Date"),
        ),
    ]