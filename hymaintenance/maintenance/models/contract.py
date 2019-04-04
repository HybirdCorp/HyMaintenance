from django.db import models
from django.db.models import F
from django.utils.timezone import datetime
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from customers.models import Company

from .credit import MaintenanceCredit
from .credit import calcul_credited_hours
from .issue import MaintenanceIssue
from .issue import calcul_consumed_minutes
from .other_models import MaintenanceType


AVAILABLE_TOTAL_TIME = 0
CONSUMMED_TOTAL_TIME = 1

MONTHLY = 0
ANNUAL = 1


class MaintenanceContractQuerySet(models.QuerySet):
    def filter_enabled(self):
        return self.filter(disabled=False).order_by(F("maintenance_type__id").asc())


class MaintenanceContract(models.Model):
    TYPE_CHOICES = (
        (AVAILABLE_TOTAL_TIME, _("Available total time")),
        (CONSUMMED_TOTAL_TIME, _("Consummed total time")),
    )

    RECURRENCE_CHOICES = ((MONTHLY, _("Monthly credit")), (ANNUAL, _("Annual credit")))

    company = models.ForeignKey(Company, verbose_name=_("Company"), on_delete=models.PROTECT, related_name="contracts")
    start = models.DateField(_("Start Date"), default=now)

    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT, related_name="contracts")
    counter_name = models.CharField(_("Name of counter"), max_length=255, default="")

    visible = models.BooleanField(_("Visible to manager"), default=True)
    disabled = models.BooleanField(_("Disable the contract"), default=False)

    total_type = models.IntegerField(_("Counter type"), choices=TYPE_CHOICES, default=AVAILABLE_TOTAL_TIME)

    reset_date = models.DateField(_("Last reset date"), null=True, blank=True)

    recurrence_start_date = models.DateField(_("Credit-recurrence start date"), null=True, blank=True)
    recurrence_last_date = models.DateField(_("Credit-recurrence last date"), null=True, blank=True)
    recurrence_next_date = models.DateField(_("Credit-recurrence next date"), null=True, blank=True)
    credit_recurrence = models.IntegerField(_("Recurrence period"), choices=RECURRENCE_CHOICES, null=True, blank=True)
    hours_to_credit = models.PositiveIntegerField(_("Hours to credit"), null=True, blank=True)

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

    def is_available_time_counter(self):
        return self.total_type == AVAILABLE_TOTAL_TIME

    def is_consumed_time_counter(self):
        return self.total_type == CONSUMMED_TOTAL_TIME

    def has_annual_credit_recurrence(self):
        return self.credit_recurrence == ANNUAL

    def has_monthly_credit_recurrence(self):
        return self.credit_recurrence == MONTHLY

    def has_credit_recurrence(self):
        return self.credit_recurrence is not None

    def get_current_issues(self):
        issues = MaintenanceIssue.objects.filter(contract=self, is_deleted=False)
        if self.reset_date:
            issues = issues.exclude(date__lt=self.reset_date)
        return issues

    def get_old_issues(self):
        if self.reset_date:
            issues = MaintenanceIssue.objects.filter(contract=self, is_deleted=False)
            issues = issues.exclude(date__gte=self.reset_date)
            return issues
        else:
            return MaintenanceIssue.objects.none()

    def get_current_credits(self):
        credits = MaintenanceCredit.objects.filter(contract=self)
        if self.reset_date:
            credits = credits.exclude(date__lt=self.reset_date)
        return credits

    def get_old_credits(self):
        if self.reset_date:
            credits = MaintenanceCredit.objects.filter(contract=self)
            credits = credits.exclude(date__gte=self.reset_date)
            return credits
        else:
            return MaintenanceCredit.objects.none()

    def get_delta_credits_minutes(self):
        if self.reset_date:
            consumed_min_sum = self.get_old_issues().aggregate(models.Sum("number_minutes"))
            consumed_min_sum = consumed_min_sum["number_minutes__sum"]
            if consumed_min_sum is None:
                consumed_min_sum = 0

            credit_hours_sum = self.get_old_credits().aggregate(models.Sum("hours_number"))
            credit_hours_sum = credit_hours_sum["hours_number__sum"]
            if credit_hours_sum is None:
                credit_hours_sum = 0

            return credit_hours_sum * 60 - consumed_min_sum
        else:
            return 0

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

    def get_recurrence_next_date(self):
        if self.has_monthly_credit_recurrence():
            return get_next_month_date(self.recurrence_start_date, self.recurrence_next_date)
        elif self.has_annual_credit_recurrence():
            return get_next_year_date(self.recurrence_start_date, self.recurrence_next_date)
        else:
            return None

    def remove_recurrence(self):
        self.credit_recurrence = None
        self.save()

    def set_annual_recurrence(self):
        self.credit_recurrence = ANNUAL
        self.set_recurrence_dates()
        self.save()

    def set_monthly_recurrence(self):
        self.credit_recurrence = MONTHLY
        self.set_recurrence_dates()
        self.save()

    def set_recurrence_dates(self):
        if now().date() >= self.recurrence_start_date:
            self.recurrence_last_date = self.recurrence_next_date = self.recurrence_start_date
            self.recurrence_next_date = self.get_recurrence_next_date()
        else:
            self.recurrence_next_date = self.recurrence_start_date

    def save(self, *args, **kwargs):
        if self.id is not None:
            self.consumed_minutes = calcul_consumed_minutes(contract=self)
            self.credited_hours = calcul_credited_hours(contract=self)
        if self.has_credit_recurrence() and self.recurrence_next_date is None:
            self.set_recurrence_dates()
        super().save(*args, **kwargs)


def get_next_month_date(start_date, old_date):
    next_month = (old_date.month + 1) % 12
    next_year = old_date.year
    if next_month == 1:
        next_year = old_date.year + 1
    next_day = start_date.day
    if not is_valid_date(next_day, next_month, next_year):
        next_day = get_last_day_of_the_month(next_month, next_year)
    return datetime(day=next_day, month=next_month, year=next_year)


def get_next_year_date(start_date, old_date):
    next_year = old_date.year + 1
    next_day = start_date.day
    if not is_valid_date(next_day, old_date.month, next_year):
        next_day = get_last_day_of_the_month(old_date.month, next_year)
    return datetime(day=next_day, month=old_date.month, year=next_year)


def is_valid_date(day, month, year):
    valid_date = True
    try:
        datetime(day=day, month=month, year=year)
    except ValueError:
        valid_date = False
    return valid_date


def get_last_day_of_the_month(month, year):
    day = 31
    while not is_valid_date(day, month, year):
        day -= 1
    return day
