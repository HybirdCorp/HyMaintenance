from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic import View

from customers.models import Company
from customers.models import MaintenanceUser
from customers.models.user import get_companies_of_operator
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceType
from maintenance.models.contract import AVAILABLE_TOTAL_TIME

from ..models import GeneralInformation


def get_maintenance_types():
    context = {"maintenance_types": MaintenanceType.objects.all().order_by("id")}
    return context


def get_context_data_dashboard_header(user):
    context = {"operators_number": MaintenanceUser.objects.get_active_operator_users_queryset().count()}
    if user.is_superuser:
        context["companies_number"] = Company.objects.all().count()
    else:
        context["companies_number"] = get_companies_of_operator(user).count()
    return context


def get_context_data_project_header(user, company):
    context = {}
    if user.is_staff:
        context["contracts"] = MaintenanceContract.objects.filter(company=company, disabled=False).order_by(
            "maintenance_type__pk"
        )
    else:
        context["contracts"] = MaintenanceContract.objects.filter(
            company=company, visible=True, disabled=False
        ).order_by("maintenance_type__pk")
    context["add_credits"] = (
        True if context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME, disabled=False).count() else False
    )
    context["company"] = company
    return context


def get_context_data_footer():
    return {"general_info": GeneralInformation.objects.all().first()}


class ViewWithCompany(View):
    slug_url_kwarg = "company_name"
    slug_field = "slug_name"

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_company()
        return super().dispatch(request, *args, **kwargs)

    def get_company(self):
        company = get_object_or_404(Company, slug_name=self.kwargs.get(self.slug_url_kwarg))
        return company

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(get_context_data_project_header(user, self.company))
        context.update(get_context_data_footer())
        return context


class IsAdminTestMixin(UserPassesTestMixin):
    def test_func(self):
        self.user = self.request.user
        return self.user.is_superuser


class IsAtLeastAllowedOperatorTestMixin(IsAdminTestMixin):
    def test_func(self):
        return super().test_func() or (self.user.is_staff and self.company in self.user.operator_for.all())


class IsAtLeastAllowedManagerTestMixin(IsAtLeastAllowedOperatorTestMixin):
    def test_func(self):
        return super().test_func() or (self.company == self.user.company)
