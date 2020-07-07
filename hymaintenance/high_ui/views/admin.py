from django.views.generic import TemplateView
from django.db.models import Count, Case, When

from customers.models.user import Company
from customers.models.user import MaintenanceUser
from maintenance.models.credit import MaintenanceCreditChoices

from .base import IsAdminTestMixin
from .base import get_context_data_dashboard_header
from .base import get_maintenance_types


class AdminView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_maintenance_types())
        context["admins"] = MaintenanceUser.objects.get_admin_users_queryset().annotate(users_number=Count("id"))
        context["operators"] = MaintenanceUser.objects.get_active_operator_users_queryset() \
            .annotate(users_number=Count("id"))
        context["active_projects"] = Company.objects.filter(is_archived=False).order_by("name") \
            .annotate(optimized_archived_issues_number=Count(Case(When(maintenanceissue__is_deleted=True, then=1)))) \
            .annotate(projects_number=Count("id"))
        context["archived_projects"] = Company.objects.filter(is_archived=True).order_by("name") \
            .annotate(optimized_archived_issues_number=Count(Case(When(maintenanceissue__is_deleted=True, then=1)))) \
            .annotate(projects_number=Count("id"))
        context["credit_choices"] = MaintenanceCreditChoices.objects.all().order_by("id")
        return context
