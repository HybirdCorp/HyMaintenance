# Generated by Django 2.0.3 on 2018-05-16 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0026_auto_20180427_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenanceconsumer',
            name='is_used',
            field=models.BooleanField(default=True),
        ),
    ]
