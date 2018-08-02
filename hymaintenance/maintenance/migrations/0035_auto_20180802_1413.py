# Generated by Django 2.0.3 on 2018-08-02 12:13

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0034_bound_credit_and_contract")]

    operations = [
        migrations.RemoveField(model_name="maintenancecredit", name="maintenance_type"),
        migrations.AlterField(
            model_name="maintenancecredit",
            name="contract",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="maintenance.MaintenanceContract"),
        ),
    ]
