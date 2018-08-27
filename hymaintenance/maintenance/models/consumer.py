
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from customers.models import Company


class MaintenanceConsumerManager(BaseUserManager):
    def get_used_consumers(self):
        return self.get_queryset().filter(is_used=True).order_by("name")


class MaintenanceConsumer(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    is_used = models.BooleanField(default=True)

    objects = MaintenanceConsumerManager()

    def __str__(self):
        return self.name
