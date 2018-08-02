import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from customers.models import Company

from .credit import MaintenanceCredit
from .issue import MaintenanceIssue
from .other_models import MaintenanceType


AVAILABLE_TOTAL_TIME = 0
CONSUMMED_TOTAL_TIME = 1


class MaintenanceContractQuerySet(models.QuerySet):
    def filter_enabled(self):
        return self.filter(disabled=False)


class MaintenanceContract(models.Model):
    TYPE_CHOICES = (
        (AVAILABLE_TOTAL_TIME, _("Available total time")),
        (CONSUMMED_TOTAL_TIME, _("Consummed total time")),
    )

    counter_name = models.CharField(_("Name of counter"), max_length=255, default="")
    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT, related_name="contracts")
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT, related_name="contracts")
    visible = models.BooleanField(_("Visible to customer user"), default=True)
    disabled = models.BooleanField(_("Disable the contract"), default=False)
    start = models.DateField(_("Start Date"), default=datetime.date.today)
    number_hours = models.PositiveIntegerField("Number of Hours by contract", default=0)
    total_type = models.IntegerField(_("Counter type"), choices=TYPE_CHOICES, default=AVAILABLE_TOTAL_TIME)

    objects = MaintenanceContractQuerySet.as_manager()

    def __str__(self):
        return "%s , %s" % (self.company, self.maintenance_type)

    def get_counter_name(self):
        return self.counter_name if self.counter_name != "" else self.maintenance_type.name

    def get_number_contract_hours(self) -> int:
        hours_sum = MaintenanceCredit.objects.filter(company=self.company, contract=self).aggregate(
            models.Sum("hours_number")
        )
        hours_sum = hours_sum["hours_number__sum"]
        if hours_sum is None:
            hours_sum = 0
        return int(self.number_hours) + hours_sum

    def get_number_contract_minutes(self) -> int:
        return self.get_number_contract_hours() * 60

    def get_number_consumed_minutes_in_month(self, date: datetime.date) -> int:
        consumed = MaintenanceIssue.objects.filter(
            company=self.company, date__month=date.month, date__year=date.year, contract=self
        ).aggregate(models.Sum("number_minutes"))
        consumed = consumed["number_minutes__sum"]
        return consumed if consumed is not None else 0

    def get_number_consumed_minutes(self) -> int:
        consumed = MaintenanceIssue.objects.filter(company=self.company, contract=self).aggregate(
            models.Sum("number_minutes")
        )
        consumed = consumed["number_minutes__sum"]
        return consumed if consumed is not None else 0

    def get_number_remaining_minutes(self) -> int:
        remaining = self.get_number_contract_minutes() - self.get_number_consumed_minutes()
        return remaining

    def get_number_credited_hours_in_month(self, date: datetime.date) -> int:
        credited = MaintenanceCredit.objects.filter(
            company=self.company, date__month=date.month, date__year=date.year, contract=self
        ).aggregate(models.Sum("hours_number"))
        credited = credited["hours_number__sum"]
        if credited is None:
            credited = 0
        if self.start.month == date.month and self.start.year == date.year:
            credited += self.number_hours
        return credited

    def get_number_consumed_hours_in_month(self, date: datetime.date) -> float:
        return self.get_number_consumed_minutes_in_month(date) / 60

    def get_number_consumed_hours(self) -> float:
        return self.get_number_consumed_minutes() / 60

    def get_number_remaining_hours(self) -> float:
        return self.get_number_remaining_minutes() / 60
