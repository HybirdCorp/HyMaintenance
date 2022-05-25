from maintenance.forms.credit import MaintenanceCreditCreateForm
from maintenance.forms.credit import MaintenanceCreditUpdateForm
from maintenance.models import MaintenanceCredit
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.credit import MaintenanceCreditChoices

from django import forms
from django.forms import modelformset_factory
from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany
from .base import get_context_data_dashboard_header
from .base import get_context_previous_page


class CreditCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceCreditCreateForm
    template_name = "high_ui/forms/create_credit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_time_contracts"] = context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME)
        hours_numbers = (credit_choice.value for credit_choice in MaintenanceCreditChoices.objects.all().order_by("id"))
        context.update({"hours_numbers": list(hours_numbers)})
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project_details", kwargs={"company_name": self.object.company.slug_name})


class CreditUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = MaintenanceCreditUpdateForm
    template_name = "high_ui/forms/update_credit.html"
    model = MaintenanceCredit

    def get_object(self, queryset=None):
        instance = self.get_queryset().get(id=self.kwargs.get("pk"))
        if not instance.contract.is_available_time_counter():
            raise Http404(_("No credit matches the given query."))
        return instance

    def get_queryset(self):
        return MaintenanceCredit.objects.filter(company=self.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_time_contracts"] = context["contracts"].filter(total_type=AVAILABLE_TOTAL_TIME)
        hours_numbers = (credit_choice.value for credit_choice in MaintenanceCreditChoices.objects.all().order_by("id"))
        context.update({"hours_numbers": list(hours_numbers)})
        context.update(get_context_previous_page(self.request))
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


class CreditChoicesUpdateView(IsAdminTestMixin, FormView):
    form_class = modelformset_factory(
        MaintenanceCreditChoices, fields=["value"], widgets={"value": forms.TextInput()}, extra=0
    )
    template_name = "high_ui/forms/update_credit_choices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["queryset"] = MaintenanceCreditChoices.objects.all().order_by("id")
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("high_ui:admin")
