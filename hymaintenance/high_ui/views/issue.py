from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from customers.models import Company
from maintenance.forms.issue import MaintenanceIssueCreateForm, MaintenanceIssueUpdateForm
from maintenance.models import IncomingChannel, MaintenanceContract, MaintenanceIssue

from .base import CreateViewWithCompany, LoginRequiredMixin, ViewWithCompany


class IssueCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceIssueCreateForm
    template_name = "high_ui/forms/add_issue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channels'] = IncomingChannel.objects.all()
        return context

    def get_success_url(self):
        return self.company.get_absolute_url()


class IssueUpdateView(LoginRequiredMixin, ViewWithCompany, UpdateView):
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
        return reverse('high_ui:issue-details', kwargs={'company_name': self.object.company.slug_name,
                                                        'company_issue_number': self.object.company_issue_number})


class IssueDetailView(LoginRequiredMixin, DetailView):
    template_name = 'high_ui/issue_details.html'
    model = MaintenanceIssue

    def get_object(self):
        company = Company.objects.filter(slug_name=self.kwargs.get('company_name')).first()
        issue = MaintenanceIssue.objects.filter(company_issue_number=self.kwargs.get('company_issue_number'), company=company).first()
        # TODO is it better to return 404? with 403 the user can kown that the asked company issue exists
        # if 403 stays, maybe we have to design a custom forbidden access page ?
        user = self.request.user

        if not user.is_staff and user.company == company:
            return issue
        if user.is_staff and company in user.operator_for.all():
            return issue
        raise PermissionDenied
