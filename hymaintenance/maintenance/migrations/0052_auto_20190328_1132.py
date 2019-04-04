# Generated by Django 2.0.13 on 2019-03-28 10:32

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0051_maintenancecontract_reset_date")]

    operations = [
        migrations.AddField(
            model_name="maintenancecontract",
            name="credit_recurrence",
            field=models.IntegerField(
                blank=True, choices=[(0, "Monthly credit"), (1, "Annual credit")], null=True, verbose_name="Recurrence"
            ),
        ),
        migrations.AddField(
            model_name="maintenancecontract",
            name="hours_to_credit",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Hours to credit"),
        ),
    ]
