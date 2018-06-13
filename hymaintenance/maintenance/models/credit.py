from django.db import models
from django.utils.translation import ugettext_lazy as _

from customers.models import Company

from .other_models import MaintenanceType


class MaintenanceCredit(models.Model):
    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT)
    date = models.DateField(_("Date of Action"))
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT)
    hours_number = models.PositiveIntegerField(u"Hours number", default=0)

    def __str__(self):
        return "%s, the %s for %s and %s hours" % (
            self.company,
            self.date.strftime("%d/%m/%Y"),
            self.maintenance_type,
            self.hours_number,
        )
