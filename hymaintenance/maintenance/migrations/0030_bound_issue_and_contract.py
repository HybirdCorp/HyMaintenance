# Generated by Django 2.0.3 on 2018-08-01 15:05

from django.db import migrations


def do_nothing(apps, schema_editor):
    pass


def link_issues_with_corresponding_contracts(apps, schema_editor):
    MaintenanceIssue = apps.get_model("maintenance", "MaintenanceIssue")
    MaintenanceContract = apps.get_model("maintenance", "MaintenanceContract")

    for issue in MaintenanceIssue.objects.all():
        contract = MaintenanceContract.objects.filter(
            company=issue.company, maintenance_type=issue.maintenance_type
        ).first()
        issue.contract = contract
        issue.save()


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0029_maintenanceissue_contract")]

    operations = [migrations.RunPython(link_issues_with_corresponding_contracts, do_nothing)]
