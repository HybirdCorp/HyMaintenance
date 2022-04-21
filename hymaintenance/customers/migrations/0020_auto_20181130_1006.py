# Generated by Django 2.0.8 on 2018-11-30 09:06

import customers.models.company

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [("customers", "0019_company_is_archived")]

    operations = [
        migrations.AddField(
            model_name="company",
            name="color",
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name="Color"),
        ),
        migrations.AddField(
            model_name="company",
            name="logo",
            field=models.ImageField(
                blank=True,
                max_length=200,
                null=True,
                upload_to=customers.models.company._get_logo_file_path,
                verbose_name="Logo",
            ),
        ),
    ]
