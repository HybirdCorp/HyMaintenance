# Generated by Django 2.0.3 on 2018-08-02 09:28

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0032_auto_20180802_1128")]

    operations = [
        migrations.AddField(
            model_name="maintenancecredit",
            name="contract",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="maintenance.MaintenanceContract"
            ),
        )
    ]
