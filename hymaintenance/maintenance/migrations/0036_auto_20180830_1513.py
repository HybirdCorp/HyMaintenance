# Generated by Django 2.0.8 on 2018-08-30 13:13

import datetime

import maintenance.models.issue

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("maintenance", "0035_auto_20180802_1413")]

    operations = [
        migrations.AlterField(
            model_name="maintenanceconsumer", name="name", field=models.CharField(max_length=255, verbose_name="Name")
        ),
        migrations.AlterField(
            model_name="maintenancecontract",
            name="number_hours",
            field=models.PositiveIntegerField(default=0, verbose_name="Credited hours"),
        ),
        migrations.AlterField(
            model_name="maintenancecontract",
            name="visible",
            field=models.BooleanField(default=True, verbose_name="Visible to manager"),
        ),
        migrations.AlterField(
            model_name="maintenancecredit",
            name="contract",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="maintenance.MaintenanceContract",
                verbose_name="Activity type",
            ),
        ),
        migrations.AlterField(
            model_name="maintenancecredit",
            name="date",
            field=models.DateField(default=datetime.date.today, verbose_name="Effective date"),
        ),
        migrations.AlterField(
            model_name="maintenancecredit",
            name="hours_number",
            field=models.PositiveIntegerField(default=0, verbose_name="Quantity"),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="answer",
            field=models.TextField(blank=True, null=True, verbose_name="Comments"),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="consumer_who_ask",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="consumers_who_asked",
                to="maintenance.MaintenanceConsumer",
                verbose_name="Author",
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="context_description_file",
            field=models.FileField(
                max_length=200,
                null=True,
                storage=maintenance.models.issue.MaintenanceIssueAttachmentStorage(),
                upload_to=maintenance.models.issue._get_context_file_path,
                verbose_name="Attachment",
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="contract",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="maintenance.MaintenanceContract",
                verbose_name="Type of activity",
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="Details"),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="number_minutes",
            field=models.PositiveIntegerField(blank=True, default=0, verbose_name="Time spent"),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="resolution_date",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Resolution date"),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="resolution_description_file",
            field=models.FileField(
                max_length=200,
                null=True,
                storage=maintenance.models.issue.MaintenanceIssueAttachmentStorage(),
                upload_to=maintenance.models.issue._get_resolution_file_path,
                verbose_name="Attachment",
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="shipping_date",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Delivery date"),
        ),
        migrations.AlterField(
            model_name="maintenanceissue",
            name="user_who_fix",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users_who_fixed",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Operator",
            ),
        ),
        migrations.AlterField(
            model_name="maintenancetype",
            name="default_visibility",
            field=models.BooleanField(default=True, verbose_name="Visible to manager"),
        ),
        migrations.AlterField(
            model_name="maintenancetype", name="name", field=models.CharField(max_length=255, verbose_name="Name")
        ),
    ]
