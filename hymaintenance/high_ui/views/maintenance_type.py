from django.urls import reverse
from django.views.generic import FormView

from maintenance.forms.other_models import MaintenanceTypeUpdateForm

from .base import IsAdminTestMixin
from .base import get_context_data_dashboard_header


class MaintenanceTypeUpdateView(IsAdminTestMixin, FormView):
    form_class = MaintenanceTypeUpdateForm
    template_name = "high_ui/forms/update_maintenance_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        return context

    def form_valid(self, form):
        form.update_maintenance_types_names()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("high_ui:admin")
