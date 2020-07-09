from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, F
from django.shortcuts import redirect
from django.views.generic import TemplateView

from customers.models import Company
from customers.models.user import get_active_companies_of_operator, MaintenanceUser
from maintenance.models import MaintenanceConsumer, MaintenanceContract

from .base import get_context_data_dashboard_header


def optimize_info_for_dashboard(queryset):
    queryset = queryset \
        .prefetch_related(Prefetch(
        "maintenanceconsumer_set",
        queryset=MaintenanceConsumer.objects.filter(is_used=True).order_by("name"),
        to_attr="consumers"
    )) \
        .prefetch_related(Prefetch(
        "managed_by",
        queryset=MaintenanceUser.objects.filter(is_staff=True, is_active=True).order_by("first_name"),
        to_attr="maintainers"
    )) \
        .prefetch_related(Prefetch(
        "maintenanceuser_set",
        queryset=MaintenanceUser.objects.filter(is_staff=False, is_superuser=False, is_active=True).order_by(
            "first_name"),
        to_attr="managers"
    )) \
        .prefetch_related(Prefetch(
        "contracts",
        queryset=MaintenanceContract.objects.filter(disabled=False).order_by(F("maintenance_type__id").asc()),
        to_attr="enabled_contracts"
    ))
    return queryset


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        return context

    def get(self, request, *args, **kwargs):
        self.user = request.user
        if self.user.has_operator_or_admin_permissions():
            context = self.get_context_data(**kwargs)
            if self.user.has_admin_permissions():
                context["companies"] = optimize_info_for_dashboard(Company.objects.filter(is_archived=False))

            else:
                context["companies"] = optimize_info_for_dashboard(get_active_companies_of_operator(self.user))
            return self.render_to_response(context)

        return redirect(self.user.company.get_absolute_url())
