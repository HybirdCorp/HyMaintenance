# Generated by Django 2.0.13 on 2019-03-19 13:41

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0050_auto_20190319_1110")]

    operations = [
        migrations.AddField(
            model_name="maintenancecontract",
            name="reset_date",
            field=models.DateField(blank=True, null=True, verbose_name="Start Date"),
        )
    ]
