from maintenance.forms.other_models import MaintenanceTypeNameUpdateForm
from maintenance.models import MaintenanceType

from django.forms import modelformset_factory
from django.urls import reverse
from django.views.generic import FormView

from .base import IsAdminTestMixin
from .base import get_context_data_dashboard_header
from .base import get_context_previous_page


class MaintenanceTypeUpdateView(IsAdminTestMixin, FormView):
    form_class = modelformset_factory(
        MaintenanceType,
        form=MaintenanceTypeNameUpdateForm,
        extra=0,
        max_num=3,
    )
    template_name = "high_ui/forms/update_maintenance_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("high_ui:admin")
