# Generated by Django 2.0.1 on 2018-02-28 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0003_auto_20180227_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancecontract',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Visible to simple user'),
        ),
        migrations.AlterField(
            model_name='maintenancetype',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='Visible to simple user'),
        ),
    ]