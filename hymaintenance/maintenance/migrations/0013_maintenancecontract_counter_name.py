# Modify by Niouby on 2018-03-27 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0012_remove_maintenancetype_css_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancecontract',
            name='counter_name',
            field=models.CharField(default='', max_length=255, verbose_name='Name of counter'),
        ),
    ]
