from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse

from customers.models import Company
from customers.models import MaintenanceUser
from customers.models.user import get_companies_of_operator
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceType
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME


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
    context["reset_counter"] = (
        True if context["contracts"].filter(total_type=CONSUMMED_TOTAL_TIME, disabled=False).count() else False
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
