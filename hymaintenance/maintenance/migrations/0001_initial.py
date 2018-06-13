# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-01 21:05
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("customers", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="IncomingChannel",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Name of Incoming Channel")),
            ],
            options={
                "verbose_name": "Maintenance's Incoming Channel",
                "verbose_name_plural": "Maintenance's Incoming Channel",
            },
        ),
        migrations.CreateModel(
            name="MaintenanceConsumer",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Consumer's Name")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="customers.Company")),
            ],
        ),
        migrations.CreateModel(
            name="MaintenanceContract",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start", models.DateField(verbose_name="Start Date")),
                ("number_hours", models.PositiveIntegerField(default=0, verbose_name="Number of Hours by contract")),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="customers.Company", verbose_name="Company"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MaintenanceCredit",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="Date of Action")),
                ("hours_number", models.PositiveIntegerField(default=0, verbose_name="Hours number")),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="customers.Company", verbose_name="Company"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MaintenanceIssue",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(default="une question", max_length=500, verbose_name="Subject")),
                ("date", models.DateField(verbose_name="Issue Date")),
                ("description", models.TextField(blank=True, null=True)),
                ("number_minutes", models.PositiveIntegerField(blank=True, default=0)),
                ("resolution_date", models.DateTimeField(blank=True, null=True)),
                ("shipping_date", models.DateTimeField(blank=True, null=True)),
                ("answer", models.TextField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="customers.Company", verbose_name="Company"
                    ),
                ),
                (
                    "consumer_who_ask",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consumers_who_asked",
                        to="maintenance.MaintenanceConsumer",
                        verbose_name="Who ask the question ?",
                    ),
                ),
                (
                    "incoming_channel",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="maintenance.IncomingChannel",
                        verbose_name="Incoming Channel",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MaintenanceType",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Name of Type")),
                (
                    "css_class",
                    models.CharField(blank=True, max_length=50, null=True, verbose_name="CSS class for HTML"),
                ),
                ("label_for_company_detailview", models.CharField(max_length=255, verbose_name="Label for HTML")),
            ],
            options={"verbose_name": "Maintenance's Type", "verbose_name_plural": "Maintenance's Types"},
        ),
        migrations.AddField(
            model_name="maintenanceissue",
            name="maintenance_type",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="maintenance.MaintenanceType"),
        ),
        migrations.AddField(
            model_name="maintenanceissue",
            name="user_who_fix",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="users_who_fixed",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Who fix the issue ? ",
            ),
        ),
        migrations.AddField(
            model_name="maintenancecredit",
            name="maintenance_type",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="maintenance.MaintenanceType"),
        ),
        migrations.AddField(
            model_name="maintenancecontract",
            name="maintenance_type",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="maintenance.MaintenanceType"),
        ),
    ]
