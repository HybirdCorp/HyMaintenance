# Generated by Django 2.0.2 on 2018-03-14 23:12

from django.db import migrations
from django.utils.translation import ugettext_lazy as _


def do_nothing(apps, schema_editor):
    pass


def create_maintenance_type_if_needed(apps, schema_editor):
    MaintenanceType = apps.get_model("maintenance", "MaintenanceType")

    MaintenanceType.objects.get_or_create(pk=1,
                                          defaults={"name": _('Support'),
                                                    "css_class": "type-support",
                                                    "label_for_company_detailview": _('Support')})
    MaintenanceType.objects.get_or_create(pk=2, defaults={"name": _('Maintenance'),
                                                          "css_class": "type-maintenance",
                                                          "label_for_company_detailview": _('Maintenance')})
    MaintenanceType.objects.get_or_create(pk=3, defaults={"name": _('Corrective'),
                                                          "css_class": "type-correction",
                                                          "label_for_company_detailview": _('Corrective')})


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0009_maintenancecontract_total_type'),
    ]

    operations = [
        migrations.RunPython(create_maintenance_type_if_needed, do_nothing),
    ]
