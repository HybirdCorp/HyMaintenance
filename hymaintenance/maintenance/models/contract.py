import datetime

from django.db import models
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from customers.models import Company

from .credit import MaintenanceCredit
from .credit import calcul_credited_hours
from .issue import MaintenanceIssue
from .issue import calcul_consumed_minutes
from .other_models import MaintenanceType


AVAILABLE_TOTAL_TIME = 0
CONSUMMED_TOTAL_TIME = 1


class MaintenanceContractQuerySet(models.QuerySet):
    def filter_enabled(self):
        return self.filter(disabled=False).order_by(F("maintenance_type__id").asc())


class MaintenanceContract(models.Model):
    TYPE_CHOICES = (
        (AVAILABLE_TOTAL_TIME, _("Available total time")),
        (CONSUMMED_TOTAL_TIME, _("Consummed total time")),
    )

    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT, related_name="contracts")
    start = models.DateField(_("Start Date"), default=datetime.date.today)

    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT, related_name="contracts")
    counter_name = models.CharField(_("Name of counter"), max_length=255, default="")

    visible = models.BooleanField(_("Visible to manager"), default=True)
    disabled = models.BooleanField(_("Disable the contract"), default=False)

    total_type = models.IntegerField(_("Counter type"), choices=TYPE_CHOICES, default=AVAILABLE_TOTAL_TIME)
    reset_date = models.DateField(_("Start Date"), null=True, blank=True)
    credited_hours = models.PositiveIntegerField(_("Credited hours"), null=True, blank=True)
    consumed_minutes = models.PositiveIntegerField(_("Credited hours"), default=0)

    email_alert = models.BooleanField(_("Email alert"), default=False)
    credited_hours_min = models.IntegerField(_("Credited hours Threshold"), default=0)
    recipient = models.ForeignKey(
        to="customers.MaintenanceUser",
        on_delete=models.PROTECT,
        related_name="referent_for",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": False, "is_superuser": False},
    )

    objects = MaintenanceContractQuerySet.as_manager()

    def __str__(self):
        return "%s , %s" % (self.company, self.maintenance_type)

    def get_current_issues(self):
        issues = MaintenanceIssue.objects.filter(contract=self, is_deleted=False)
        if self.reset_date:
            issues = issues.exclude(date__lt=self.reset_date)
        return issues

    def get_counter_name(self):
        return self.counter_name if self.counter_name != "" else self.maintenance_type.name

    def get_number_contract_hours(self) -> int:
        return self.credited_hours

    def get_number_contract_minutes(self) -> int:
        return self.get_number_contract_hours() * 60

    def get_number_consumed_minutes(self) -> int:
        return self.consumed_minutes

    def get_number_consumed_hours(self) -> float:
        return self.get_number_consumed_minutes() / 60

    def get_number_remaining_minutes(self) -> int:
        remaining = self.get_number_contract_minutes() - self.get_number_consumed_minutes()
        return remaining

    def get_number_remaining_hours(self) -> float:
        return self.get_number_remaining_minutes() / 60

    def get_number_consumed_minutes_in_month(self, date: datetime.date) -> int:
        consumed = MaintenanceIssue.objects.filter(
            company=self.company, date__month=date.month, date__year=date.year, contract=self, is_deleted=False
        ).aggregate(models.Sum("number_minutes"))
        consumed = consumed["number_minutes__sum"]
        return consumed if consumed is not None else 0

    def get_number_consumed_hours_in_month(self, date: datetime.date) -> float:
        return self.get_number_consumed_minutes_in_month(date) / 60

    def get_number_credited_hours_in_month(self, date: datetime.date) -> int:
        credited = MaintenanceCredit.objects.filter(
            company=self.company, date__month=date.month, date__year=date.year, contract=self
        ).aggregate(models.Sum("hours_number"))
        credited = credited["hours_number__sum"]
        if credited is None:
            credited = 0
        return credited

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.consumed_minutes = calcul_consumed_minutes(contract=self)
            self.credited_hours = calcul_credited_hours(contract=self)
        super().save(*args, **kwargs)
