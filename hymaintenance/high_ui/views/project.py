from datetime import datetime
from datetime import timedelta

from django import forms
from django.forms import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import UpdateView

from customers.forms.company import ProjectCustomizeForm
from customers.forms.project import ProjectListArchiveForm
from customers.forms.project import ProjectListUnarchiveForm
from customers.models import Company
from maintenance.forms.project import ProjectCreateForm
from maintenance.forms.project import ProjectUpdateForm
from maintenance.forms.recurrence import RecurrenceContractsModelForm
from maintenance.formsets.recurrence import RecurrenceContractsModelFormSet
from maintenance.models import MaintenanceContract
from maintenance.models import MaintenanceCredit
from maintenance.models import MaintenanceIssue
from maintenance.models.contract import AVAILABLE_TOTAL_TIME

from .base import IsAdminTestMixin, ViewWithCompanyBis
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


class ProjectDetailsView(ViewWithCompanyBis, IsAtLeastAllowedManagerTestMixin, DetailView):
    template_name = "high_ui/company_details.html"
    model = Company
    slug_url_kwarg = "company_name"
    slug_field = "slug_name"

    def get_ordered_issues_and_credits(self, month, contracts):
        issues = self.get_maintenance_issues(month, contracts)
        credits = self.get_maintenance_credits(month, contracts)

        events = [
            {
                "type": "issue",
                "css_class": issue.contract.maintenance_type.css_class,
                "date": issue.date,
                "number_minutes": issue.number_minutes,
                "counter_name": issue.get_counter_name,
                "slug_name": issue.company.slug_name,
                "company_issue_number": issue.company_issue_number,
                "subject": issue.subject,
            }
            for issue in issues
        ]

        events = events + [
            {
                "type": "credit",
                "css_class": credit.contract.maintenance_type.css_class,
                "date": credit.date,
                "hours_number": credit.hours_number,
                "counter_name": credit.get_counter_name,
                "slug_name": credit.company.slug_name,
                "id": credit.id,
                "subject": credit.subject,
            }
            for credit in credits
        ]
        events.sort(key=lambda item: item["date"], reverse=True)

        return issues.count(), events

    def get_maintenance_issues(self, month, contracts):
        return MaintenanceIssue.objects.filter(
            contract__in=contracts,
            company_id=self.company,
            date__month=month.month,
            date__year=month.year,
            is_deleted=False,
        ).select_related("contract__maintenance_type")

    def get_maintenance_credits(self, month, contracts):
        return MaintenanceCredit.objects.filter(
            contract__in=contracts, company_id=self.company, date__month=month.month, date__year=month.year
        ).select_related("contract__maintenance_type")

    def get_last_months(self, start=datetime.now()):
        last_month = start - timedelta(days=(start.day + 1))
        months = [start, last_month]
        for i in range(self.company.displayed_month_number - 2):
            last_month = last_month - timedelta(days=31)
            months.append(last_month)
        return months

    @staticmethod
    def get_contract_month_information(month, contract):
        consumed_minutes = 0
        for e in contract.consumed_minutes_by_months:
            if e[0] == month.year and e[1] == month.month:
                consumed_minutes = e[2]
                break
        credited_hours = 0
        for e in contract.credited_hours_by_months:
            if e[0] == month.year and e[1] == month.month:
                credited_hours = e[2]
                break
        return (
            contract,
            consumed_minutes,
            credited_hours,
        )

    def get_contracts_month_information(self, month, contracts):
        info_contracts = []
        for contract in contracts:
            info_contracts.append(self.get_contract_month_information(month, contract))
        return info_contracts

    def get_activities(self, months, contracts):
        activities = []
        for month in months:
            info_contract = self.get_contracts_month_information(month, contracts)
            activities.append((month, info_contract))
        return activities

    def get_history(self, months, contracts):
        history = []
        for month in months:
            info_contract = self.get_contracts_month_information(month, contracts)
            issues_count, info_events = self.get_ordered_issues_and_credits(month, contracts)
            history.append((month, issues_count, info_contract, info_events))
        return history

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        contracts = context["contracts"]

        months = self.get_last_months()
        context["activities"] = self.get_activities(months, contracts)
        context["history"] = self.get_history(months, contracts)

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
        fields=["email_alert", "credited_hours_min", "recipient", "id"],
        widgets={
            "email_alert": forms.HiddenInput(),
            "credited_hours_min": forms.TextInput(),
            "id": forms.HiddenInput(attrs={"readonly": True}),
        },
        labels={"credited_hours_min": _("Hour threshold"), "recipient": _("To contact")},
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
