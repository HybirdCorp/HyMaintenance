from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic import View

from customers.models import Company
from customers.models import MaintenanceUser
from customers.models.user import get_companies_of_operator
from maintenance.models import MaintenanceContract


def get_context_data_dashboard_header(user):
    context = {}
    context["operators_number"] = MaintenanceUser.objects.get_active_operator_users_queryset().count()
    if user.is_superuser:
        context["companies_number"] = Company.objects.all().count()
    else:
        context["companies_number"] = get_companies_of_operator(user).count()
    return context


def get_context_data_project_header(company):
    context = {}
    context["contracts"] = MaintenanceContract.objects.filter(company=company, disabled=False)
    context["company"] = company
    return context


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
        context.update(get_context_data_project_header(self.company))
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
