
from django.db import models
from django.utils.translation import ugettext_lazy as _

from customers.models import Company


class MaintenanceConsumer(models.Model):
    name = models.CharField(_("Consumer's Name"), max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
