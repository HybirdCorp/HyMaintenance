# Generated by Django 2.0.8 on 2018-11-14 15:54

import maintenance.models.issue

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0039_maintenancecontract_email_alert")]

    operations = [
        migrations.AddField(
            model_name="maintenanceissue",
            name="is_deleted",
            field=models.BooleanField(default=False, verbose_name="Deleted"),
        ),
        migrations.AlterField(
            model_name="maintenancecontract",
            name="recipient",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"is_staff": False},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="referent_for",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="context_description_file",
            field=models.FileField(
                blank=True,
                max_length=200,
                null=True,
                storage=maintenance.models.issue.MaintenanceIssueAttachmentStorage(),
                upload_to=maintenance.models.issue._get_context_file_path,
                verbose_name="Attachment",
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="resolution_description_file",
            field=models.FileField(
                blank=True,
                max_length=200,
                null=True,
                storage=maintenance.models.issue.MaintenanceIssueAttachmentStorage(),
                upload_to=maintenance.models.issue._get_resolution_file_path,
                verbose_name="Attachment",
            ),
        ),
    ]
