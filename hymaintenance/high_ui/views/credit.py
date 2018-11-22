from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from maintenance.forms.credit import MaintenanceCreditCreateForm
from maintenance.forms.credit import MaintenanceCreditUpdateForm
from maintenance.models import MaintenanceCredit
from maintenance.models.contract import AVAILABLE_TOTAL_TIME

from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany


class CreditCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceCreditCreateForm
    template_name = "high_ui/forms/create_credit.html"

    def dispatch(self, request, *args, **kwargs):
        self.hours_step = 8
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_time_contracts"] = context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME)
        context.update({"hours_numbers": range(self.hours_step, 6 * self.hours_step, self.hours_step)})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        kwargs["hours_number_initial"] = self.hours_step
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project_details", kwargs={"company_name": self.object.company.slug_name})


class CreditUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = MaintenanceCreditUpdateForm
    template_name = "high_ui/forms/update_credit.html"
    model = MaintenanceCredit

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        return MaintenanceCredit.objects.filter(company=self.company)

    def dispatch(self, request, *args, **kwargs):
        self.hours_step = 8
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_time_contracts"] = context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME)
        context.update({"hours_numbers": range(self.hours_step, 6 * self.hours_step, self.hours_step)})
        return context

    def get_success_url(self):
        return reverse("high_ui:project_details", kwargs={"company_name": self.object.company.slug_name})


class CreditDeleteView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, RedirectView):
    permanent = True
    query_string = True
    pattern_name = "high_ui:project_details"

    def get_object(self, queryset=None):
        return self.get_queryset().filter(pk=self.kwargs.get("pk")).first()

    def get_queryset(self):
        return MaintenanceCredit.objects.filter(company=self.company)

    def get_redirect_url(self, *args, **kwargs):
        credit = self.get_object()
        credit.delete()
        del kwargs["pk"]
        return super().get_redirect_url(*args, **kwargs)
