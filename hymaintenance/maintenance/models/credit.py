import datetime

from django.db import models
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from customers.models import Company

from .utils import get_counter_name


class MaintenanceCredit(models.Model):
    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT)
    date = models.DateField(_("Effective date"), default=datetime.date.today)
    contract = models.ForeignKey(
        to="maintenance.MaintenanceContract", verbose_name=_("Activity type"), on_delete=models.PROTECT
    )
    hours_number = models.PositiveIntegerField(_("Quantity"), default=0)
    subject = models.CharField(_("Subject"), null=True, blank=True, max_length=500)

    def __str__(self):
        return "%s, the %s for %s and %s hours" % (
            self.company,
            self.date.strftime("%d/%m/%Y"),
            self.contract,
            self.hours_number,
        )

    def get_counter_name(self):
        return get_counter_name(self)


@receiver(post_save, sender=MaintenanceCredit, dispatch_uid="update_credited_hours")
def update_credited_hours_after_save(sender, instance, **kwargs):
    instance.contract.credited_hours = calcul_credited_hours(contract=instance.contract)
    instance.contract.save()


@receiver(post_delete, sender=MaintenanceCredit, dispatch_uid="update_credited_hours")
def update_credited_hours_after_delete(sender, instance, **kwargs):
    instance.contract.credited_hours = calcul_credited_hours(contract=instance.contract)
    instance.contract.save()


def calcul_credited_hours(contract):
    hours_sum = MaintenanceCredit.objects.filter(contract=contract).aggregate(models.Sum("hours_number"))
    hours_sum = hours_sum["hours_number__sum"]
    if hours_sum is None:
        hours_sum = 0
    return hours_sum


class MaintenanceCreditChoices(models.Model):
    value = models.IntegerField(_("Value"))

    def __str__(self):
        return "{}".format(self.value)
