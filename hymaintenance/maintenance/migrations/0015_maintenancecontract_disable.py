# Generated by Django 2.0.3 on 2018-04-04 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0014_auto_20180330_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancecontract',
            name='disable',
            field=models.BooleanField(default=False, verbose_name='Disable the contract'),
        ),
    ]
