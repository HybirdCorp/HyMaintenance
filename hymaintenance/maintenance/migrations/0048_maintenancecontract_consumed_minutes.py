# Generated by Django 2.0.13 on 2019-03-18 16:29

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0047_auto_20190306_1455")]

    operations = [
        migrations.AddField(
            model_name="maintenancecontract",
            name="consumed_minutes",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Credited hours"),
        )
    ]