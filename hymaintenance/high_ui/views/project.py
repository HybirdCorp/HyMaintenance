from datetime import datetime

from customers.forms.company import ProjectCustomizeForm
from customers.forms.project import ProjectListArchiveForm
from customers.forms.project import ProjectListUnarchiveForm
from customers.models import Company
from dateutil.relativedelta import relativedelta
from maintenance.forms.email import EmailAlertUpdateForm
from maintenance.forms.project import ProjectCreateForm
from maintenance.forms.project import ProjectUpdateForm
from maintenance.forms.recurrence import RecurrenceContractsModelForm
from maintenance.formsets.recurrence import RecurrenceContractsModelFormSet
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceCredit
from maintenance.models import MaintenanceIssue
from maintenance.models.contract import AVAILABLE_TOTAL_TIME

from django import forms
from django.forms import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import UpdateView

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedManagerTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany
from .base import get_context_data_dashboard_header
from .base import get_context_previous_page
from .base import get_maintenance_types


class ProjectCreateView(IsAdminTestMixin, FormView):
    form_class = ProjectCreateForm
    template_name = "high_ui/forms/create_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def form_valid(self, form):
        form.create_company_and_contracts()
        return super().form_valid(form)


class ProjectUpdateView(IsAdminTestMixin, ViewWithCompany, FormView):
    form_class = ProjectUpdateForm
    template_name = "high_ui/forms/update_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.update_company_and_contracts()
        return super().form_valid(form)


class ProjectDetailsView(ViewWithCompany, IsAtLeastAllowedManagerTestMixin, DetailView):
    template_name = "high_ui/company_details.html"
    model = Company
    slug_url_kwarg = "company_name"
    slug_field = "slug_name"

    def initialize_history_data_structure(self, contracts):
        current_month = datetime.strptime(datetime.now().strftime('%m/%Y'), '%m/%Y').date()
        month = None
        history = {}
        for i in range(self.company.displayed_month_number):
            month = current_month - relativedelta(months=i)
            contracts_info = {}
            for contract in contracts:
                contracts_info[str(contract.id)] = {
                    "css_class": contract.css_class,
                    "counter_name": contract.displayed_counter_name,
                    "is_available_time_counter": contract.is_available_time_counter(),
                    "consumed": 0,
                    "credited": 0
                }
            history[month] = {
                "contracts": contracts_info,
                "events_count": 0,
                "events": []
            }
        return month, history

    def get_history(self, contracts):
        # initialize section for each months of this history
        last_month, history = self.initialize_history_data_structure(contracts)

        # get passed events lint of the asked months
        issues = MaintenanceIssue.objects.home_history_values(self.company, contracts, last_month)
        credits = MaintenanceCredit.objects.home_history_values(self.company, contracts, last_month)

        events = list(issues) + list(credits)
        events.sort(key=lambda item: item["date"], reverse=True)

        # format history info
        for event in events:
            month = datetime.strptime(event["date"].strftime('%m/%Y'), '%m/%Y').date()

            history[month]["events_count"] += 1
            history[month]["events"].append(event)

            if event["type"] == "issue":
                history[month]["contracts"][str(event["contract"])]["consumed"] += event["number_minutes"]
            else:
                history[month]["contracts"][str(event["contract"])]["credited"] += event["hours_number"]

        return history

    def get_forecast(self, contracts):
        # get future events list
        issues = MaintenanceIssue.objects.home_forecast_values(self.company, contracts)
        credits = MaintenanceCredit.objects.home_forecast_values(self.company, contracts)

        events = list(issues) + list(credits)
        events.sort(key=lambda item: item["date"])

        # format forecast info
        forecast = {}
        for event in events:
            month = datetime.strptime(event["date"].strftime('%m/%Y'), '%m/%Y').date()
            if month not in forecast:
                contracts_info = {}
                for contract in contracts:
                    contracts_info[str(contract.id)] = {
                        "css_class": contract.css_class,
                        "counter_name": contract.displayed_counter_name,
                        "is_available_time_counter": contract.is_available_time_counter(),
                        "consumed": 0,
                        "credited": 0
                    }
                forecast[month] = {
                    "contracts": contracts_info,
                    "events_count": 1,
                    "events": [event, ]
                }
            else:
                forecast[month]["events_count"] += 1
                forecast[month]["events"].append(event)

            if event["type"] == "issue":
                forecast[month]["contracts"][str(event["contract"])]["consumed"] += event["number_minutes"]
            else:
                forecast[month]["contracts"][str(event["contract"])]["credited"] += event["hours_number"]

        return forecast

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        contracts = context["contracts"]

        context["history"] = self.get_history(contracts)
        context["forecast"] = self.get_forecast(contracts)

        return context


class ProjectListArchiveView(IsAdminTestMixin, FormView):
    form_class = ProjectListArchiveForm
    template_name = "high_ui/forms/archive_projects.html"
    success_url = "/high_ui/admin/"  # TMP

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context["projects_number"] = Company.objects.filter(is_archived=False).count()
        context.update(get_context_previous_page(self.request))
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProjectListUnarchiveView(IsAdminTestMixin, FormView):
    form_class = ProjectListUnarchiveForm
    template_name = "high_ui/forms/unarchive_projects.html"
    success_url = "/high_ui/admin/"  # TMP

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context["projects_number"] = Company.objects.filter(is_archived=True).count()
        context.update(get_context_previous_page(self.request))
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class EmailAlertUpdateView(ViewWithCompany, IsAtLeastAllowedManagerTestMixin, FormView):
    form_class = modelformset_factory(
        MaintenanceContract,
        form=EmailAlertUpdateForm,
        extra=0,
    )
    template_name = "high_ui/forms/update_email_alert.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.user.has_operator_or_admin_permissions():
            kwargs["queryset"] = self.company.contracts.filter(
                disabled=False, total_type=AVAILABLE_TOTAL_TIME
            ).order_by("maintenance_type_id")
        else:
            kwargs["queryset"] = self.company.contracts.filter(
                disabled=False, total_type=AVAILABLE_TOTAL_TIME, visible=True
            ).order_by("maintenance_type_id")
        return kwargs

    def get_form(self):
        formset = super().get_form()
        for form in formset:
            form.fields["recipient"].queryset = form.fields["recipient"].queryset.filter(company=self.company)
            form.counter_name = form.instance.get_counter_name()
        return formset

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProjectResetCountersView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
    form_class = modelformset_factory(
        MaintenanceContract,
        fields=["reset_date", "id"],
        widgets={"id": forms.HiddenInput(attrs={"readonly": True})},
        labels={"reset_date": _("Reset date")},
        extra=0,
    )
    template_name = "high_ui/forms/reset_contracts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["queryset"] = self.company.contracts.filter(disabled=False).order_by("maintenance_type_id")
        return kwargs

    def get_form(self):
        formset = super().get_form()
        for form in formset:
            form.counter_name = form.instance.get_counter_name()
        return formset

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.company.get_absolute_url()


class ProjectCreditRecurrenceUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
    form_class = modelformset_factory(
        model=MaintenanceContract, formset=RecurrenceContractsModelFormSet, form=RecurrenceContractsModelForm, extra=0
    )
    template_name = "high_ui/forms/update_credit_recurrence.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        for sub_form in form:
            sub_form.instance.set_recurrence_dates_and_create_all_old_credit_occurrences()
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.company.get_absolute_url()


class ProjectCustomizeView(IsAdminTestMixin, ViewWithCompany, UpdateView):
    form_class = ProjectCustomizeForm
    template_name = "high_ui/forms/customize_project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def get_object(self, queryset=None):
        return self.company

    def get_success_url(self):
        return self.company.get_absolute_url()
