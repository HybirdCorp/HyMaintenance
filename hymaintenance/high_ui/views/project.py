from datetime import datetime
from datetime import timedelta

from django.views.generic import DetailView
from django.views.generic import FormView

from customers.models import Company
from maintenance.forms.project import ProjectCreateForm
from maintenance.forms.project import ProjectUpdateForm
from maintenance.models import MaintenanceCredit
from maintenance.models import MaintenanceIssue

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedManagerTestMixin
from .base import ViewWithCompany
from .base import get_context_data_dashboard_header
from .base import get_maintenance_types


class ProjectCreateView(IsAdminTestMixin, FormView):
    form_class = ProjectCreateForm
    template_name = "high_ui/forms/create_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_maintenance_types())
        context.update(get_context_data_dashboard_header(self.user))
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
            }
            for credit in credits
        ]
        events.sort(key=lambda item: item["date"], reverse=True)

        return issues.count(), events

    def get_maintenance_issues(self, month, contracts):
        return MaintenanceIssue.objects.filter(
            contract__in=contracts, company_id=self.company, date__month=month.month, date__year=month.year
        )

    def get_maintenance_credits(self, month, contracts):
        return MaintenanceCredit.objects.filter(
            contract__in=contracts, company_id=self.company, date__month=month.month, date__year=month.year
        )

    def get_last_months(self, start=datetime.now()):
        last_month = start - timedelta(days=(start.day + 1))
        months = [start, last_month]
        for i in range(4):
            last_month = last_month - timedelta(days=31)
            months.append(last_month)
        return months

    def get_contract_month_informations(self, month, contract):
        return (
            contract,
            contract.get_number_consumed_minutes_in_month(month),
            contract.get_number_credited_hours_in_month(month),
        )

    def get_contracts_month_informations(self, month, contracts):
        info_contracts = []
        for contract in contracts:
            info_contracts.append(self.get_contract_month_informations(month, contract))
        return info_contracts

    def get_activities(self, months, contracts):
        activities = []
        for month in months:
            info_contract = self.get_contracts_month_informations(month, contracts)
            activities.append((month, info_contract))
        return activities

    def get_history(self, months, contracts):
        history = []
        for month in months:
            info_contract = self.get_contracts_month_informations(month, contracts)
            issues_count, info_events = self.get_ordered_issues_and_credits(month, contracts)
            history.append((month, issues_count, info_contract, info_events))
        return history

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        self.company = self.object
        contracts = context["contracts"]

        months = self.get_last_months()
        context["activities"] = self.get_activities(months, contracts)
        context["history"] = self.get_history(months, contracts)

        return context
