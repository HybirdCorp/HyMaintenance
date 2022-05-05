from customers.models.user import Company
from customers.models.user import MaintenanceUser
from maintenance.models.credit import MaintenanceCreditChoices

from django.db.models import Case
from django.db.models import Count
from django.db.models import When
from django.views.generic import TemplateView

from .base import IsAdminTestMixin
from .base import get_context_data_dashboard_header
from .base import get_maintenance_types


class AdminView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_maintenance_types())

        context["admins"] = MaintenanceUser.objects.get_admin_users_queryset()
        context["admins_number"] = context["admins"].aggregate(Count("id"))["id__count"]

        context["operators"] = MaintenanceUser.objects.get_active_operator_users_queryset()
        context["operators_number"] = context["operators"].aggregate(Count("id"))["id__count"]

        context["active_projects"] = Company.objects.filter(is_archived=False).order_by("name").annotate(
            archived_issues_number=Count(Case(When(maintenanceissue__is_deleted=True, then=1))))
        context["active_projects_number"] = context["active_projects"].aggregate(Count("id"))["id__count"]

        context["archived_projects"] = Company.objects.filter(is_archived=True).order_by("name")
        context["archived_projects_number"] = context["archived_projects"].aggregate(Count("id"))["id__count"]

        context["credit_choices"] = MaintenanceCreditChoices.objects.all().order_by("id")
        return context
