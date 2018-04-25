# Generated by Django 2.0.3 on 2018-04-24 11:30

from django.db import migrations, models

import maintenance.models.issue


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0024_auto_20180417_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenanceissue',
            name='context_description_file',
            field=models.FileField(max_length=200, null=True, upload_to=maintenance.models.issue._get_file_path),
        ),
        migrations.AlterField(
            model_name='maintenanceissue',
            name='resolution_description_file',
            field=models.FileField(max_length=200, null=True, upload_to=maintenance.models.issue._get_file_path),
        ),
    ]
