# Generated by Django 2.0.13 on 2019-03-18 16:30

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0048_maintenancecontract_consumed_minutes")]

    operations = [
        migrations.AlterField(
            model_name="maintenancecontract",
            name="consumed_minutes",
            field=models.PositiveIntegerField(default=0, verbose_name="Credited hours"),
        )
    ]