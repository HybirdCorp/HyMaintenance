from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse

from customers.models import Company
from customers.models import MaintenanceUser
from customers.models.user import get_companies_of_operator
from maintenance.models import MaintenanceContract, MaintenanceCredit
from maintenance.models import MaintenanceType
from maintenance.models.contract import AVAILABLE_TOTAL_TIME


def get_maintenance_types():
    context = {"maintenance_types": MaintenanceType.objects.all().order_by("id")}
    return context


def get_context_previous_page(request):
    previous_page = request.META.get("HTTP_REFERER")
    if not previous_page or reverse("login") in previous_page:
        previous_page = reverse("high_ui:dashboard")
    return {"previous_page": previous_page}


def get_context_data_dashboard_header(user):
    context = {
        "all_types_operators_number": MaintenanceUser.objects.get_active_all_types_operator_users_queryset().count()
    }
    if user.has_admin_permissions():
        context["companies_number"] = Company.objects.filter(is_archived=False).count()
    else:
        context["companies_number"] = get_companies_of_operator(user).filter(is_archived=False).count()
    return context


def get_context_data_project_header(user, company):
    context = {}
    if user.has_operator_or_admin_permissions():
        context["contracts"] = MaintenanceContract.objects.filter_enabled().filter(company=company)
    else:
        context["contracts"] = MaintenanceContract.objects.filter_enabled_and_visible().filter(company=company)
    context["add_credits"] = (
        True if context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME, disabled=False).count() else False
    )
    context["company"] = company
    return context


from datetime import datetime
from datetime import timedelta
def get_last_months(company, start=datetime.now()):
    last_month = start - timedelta(days=(start.day + 1))
    months = [start, last_month]
    for i in range(company.displayed_month_number - 2):
        last_month = last_month - timedelta(days=31)
        months.append(last_month)
    return months

"""
from django.db import models
from .issue import MaintenanceIssue
def get_number_consumed_minutes_in_month(contract, date: datetime.date) -> int:
    consumed = MaintenanceIssue.objects.filter(
        company=contract.company, date__month=date.month, date__year=date.year, contract=contract, is_deleted=False
    ).aggregate(models.Sum("number_minutes"))
    consumed = consumed["number_minutes__sum"]
    return consumed if consumed is not None else 0
"""

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from maintenance.models import MaintenanceIssue
def get_context_data_project_header_bis(user, company):
    context = {}
    min_date = (datetime.now() - relativedelta(months=company.displayed_month_number)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if user.has_operator_or_admin_permissions():

        context["contracts"] = MaintenanceContract.objects.filter_enabled().filter(company=company)
    else:
        context["contracts"] = MaintenanceContract.objects.filter_enabled().filter(company=company)

    for contract in context["contracts"]:
        contract.consumed_minutes_by_months = MaintenanceIssue.objects \
            .filter(company=contract.company, contract=contract, date__gte=min_date, is_deleted=False) \
            .values_list("date__year", "date__month") \
            .annotate(consumed_minutes_by_months=Sum("number_minutes"), ) \
            .order_by("date__year", "date__month")

        contract.credited_hours_by_months = MaintenanceCredit.objects \
            .filter(company=contract.company, contract=contract, date__gte=min_date) \
            .values_list("date__year", "date__month") \
            .annotate(consumed_minutes_by_months=Sum("hours_number"), ) \
            .order_by("date__year", "date__month")

    context["add_credits"] = (
        True if context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME, disabled=False).count() else False
    )
    context["company"] = company
    return context


class ViewWithCompany:
    slug_url_kwarg = "company_name"
    slug_field = "slug_name"
    _company = None

    @property
    def company(self):
        if not self._company:
            self._company = get_object_or_404(
                Company, is_archived=False, slug_name=self.kwargs.get(self.slug_url_kwarg)
            )
        return self._company

    @company.setter
    def company(self, value):
        self._company = value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(get_context_data_project_header(user, self.company))
        return context


class ViewWithCompanyBis(ViewWithCompany):
      def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(get_context_data_project_header_bis(user, self.company))
        return context


class IsAdminTestMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        self.user = self.request.user
        return self.user.has_admin_permissions()


class IsAtLeastAllowedOperatorTestMixin(IsAdminTestMixin):
    def test_func(self):
        return super().test_func() or (
            self.user.has_operator_permissions() and self.company in self.user.operator_for.all()
        )


class IsAtLeastAllowedManagerTestMixin(IsAtLeastAllowedOperatorTestMixin):
    def test_func(self):
        return super().test_func() or (self.company == self.user.company)
