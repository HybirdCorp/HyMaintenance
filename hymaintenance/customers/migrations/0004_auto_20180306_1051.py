# Generated by Django 2.0.2 on 2018-03-06 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_auto_20180227_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='maintenance_contact',
            field=models.CharField(default='', max_length=500, verbose_name='name of internal contact'),
        ),
    ]