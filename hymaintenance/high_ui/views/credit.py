from django.urls import reverse
from django.views.generic import CreateView

from maintenance.forms.credit import MaintenanceCreditCreateForm
from maintenance.models.contract import AVAILABLE_TOTAL_TIME

from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany
from .base import get_context_data_footer


class CreditCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceCreditCreateForm
    template_name = "high_ui/forms/create_credit.html"

    def dispatch(self, request, *args, **kwargs):
        self.hours_step = 8
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_time_contracts"] = context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME)
        context.update(get_context_data_footer())
        context.update({"hours_numbers": range(self.hours_step, 6 * self.hours_step, self.hours_step)})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        kwargs["hours_number_initial"] = self.hours_step
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project_details", kwargs={"company_name": self.object.company.slug_name})
