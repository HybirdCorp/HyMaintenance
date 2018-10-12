from django.views.generic import TemplateView

from customers.models.user import MaintenanceUser

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
        context["operators"] = MaintenanceUser.objects.get_active_operator_users_queryset()
        return context
