# Generated by Django 2.0.1 on 2018-03-01 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0005_auto_20180228_1126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenancecontract',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Visible to customer user'),
        ),
        migrations.AlterField(
            model_name='maintenancetype',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Visible to customer user'),
        ),
    ]
