# Generated by Django 2.0.3 on 2018-04-06 13:04

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0017_auto_20180404_1513")]

    operations = [
        migrations.AddField(model_name="maintenanceissue", name="number", field=models.PositiveIntegerField(null=True))
    ]
