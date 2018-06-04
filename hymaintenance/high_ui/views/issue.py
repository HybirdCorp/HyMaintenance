from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView

from maintenance.forms.issue import MaintenanceIssueCreateForm, MaintenanceIssueUpdateForm
from maintenance.models import IncomingChannel, MaintenanceContract, MaintenanceIssue

from .base import IsAtLeastAllowedManagerTestMixin, IsAtLeastAllowedOperatorTestMixin, ViewWithCompany


class IssueCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceIssueCreateForm
    template_name = "high_ui/forms/create_issue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channels'] = IncomingChannel.objects.all()
        context['company'] = self.company
        contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        context['contracts'] = contracts
        return context

    def get_success_url(self):
        return self.company.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.company
        return kwargs


class IssueUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = MaintenanceIssueUpdateForm
    template_name = "high_ui/forms/update_issue.html"
    model = MaintenanceIssue

    def get_object(self):
        return self.get_queryset().filter(company_issue_number=self.kwargs.get('company_issue_number')).first()

    def get_queryset(self):
        return MaintenanceIssue.objects.filter(company=self.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channels'] = IncomingChannel.objects.all()

        contracts = MaintenanceContract.objects.filter(company=self.object.company_id, disabled=False)
        context['contracts'] = contracts
        return context

    def get_success_url(self):
        return reverse('high_ui:project-issue_details',
                       kwargs={'company_name': self.object.company.slug_name,
                               'company_issue_number': self.object.company_issue_number})


class IssueDetailView(ViewWithCompany, IsAtLeastAllowedManagerTestMixin, DetailView):
    template_name = 'high_ui/issue_details.html'
    model = MaintenanceIssue

    def get_object(self):
        return MaintenanceIssue.objects.filter(company_issue_number=self.kwargs.get('company_issue_number'), company=self.company).first()
