# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-01 21:05
from __future__ import unicode_literals

import customers.fields
import customers.models.user

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth", "0008_alter_user_username_max_length")]

    operations = [
        migrations.CreateModel(
            name="MaintenanceUser",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Creation date")),
                ("modified", models.DateTimeField(auto_now=True, verbose_name="Last modification date")),
                ("first_name", models.CharField(blank=True, max_length=50, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=50, verbose_name="last name")),
                (
                    "email",
                    customers.fields.LowerCaseEmailField(
                        db_index=True,
                        error_messages={"unique": "A user with that username already exists."},
                        max_length=254,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",  # noqa : E501
                        verbose_name="active",
                    ),
                ),
            ],
            options={"abstract": False},
            managers=[("objects", customers.models.user.MaintenanceUserManager())],
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                ("name_for_site", models.CharField(max_length=255, verbose_name="name")),
                ("maintenance_contact", models.CharField(max_length=500, verbose_name="name of internal contact")),
            ],
        ),
        migrations.AddField(
            model_name="maintenanceuser",
            name="company",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="customers.Company"
            ),
        ),
        migrations.AddField(
            model_name="maintenanceuser",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",  # noqa : E501
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="maintenanceuser",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
    ]
