# Generated by Django 2.0.3 on 2018-04-04 13:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0016_create_disabled_contracts")]

    operations = [migrations.RenameField(model_name="maintenancecontract", old_name="disable", new_name="disabled")]
