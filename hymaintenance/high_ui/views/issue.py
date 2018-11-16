from django.http import Http404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from maintenance.forms.issue import MaintenanceIssueCreateForm
from maintenance.forms.issue import MaintenanceIssueUpdateForm
from maintenance.models import MaintenanceIssue

from .base import IsAtLeastAllowedManagerTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany


class IssueCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceIssueCreateForm
    template_name = "high_ui/forms/create_issue.html"

    def get_success_url(self):
        return self.company.get_absolute_url()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs


class IssueUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = MaintenanceIssueUpdateForm
    template_name = "high_ui/forms/update_issue.html"
    model = MaintenanceIssue

    def get_object(self, queryset=None):
        issue = self.get_queryset().filter(company_issue_number=self.kwargs.get("company_issue_number")).first()
        if issue.is_deleted:
            raise Http404("No issue matches the given query.")
        else:
            return issue

    def get_queryset(self):
        return MaintenanceIssue.objects.filter(company=self.company)

    def get_success_url(self):
        return reverse(
            "high_ui:project-issue_details",
            kwargs={
                "company_name": self.object.company.slug_name,
                "company_issue_number": self.object.company_issue_number,
            },
        )


class IssueDetailView(ViewWithCompany, IsAtLeastAllowedManagerTestMixin, DetailView):
    template_name = "high_ui/issue_details.html"
    model = MaintenanceIssue

    def get_object(self, queryset=None):
        issue = self.get_queryset().filter(company_issue_number=self.kwargs.get("company_issue_number")).first()
        if issue.is_deleted:
            raise Http404("No issue matches the given query.")
        else:
            return issue

    def get_queryset(self):
        return MaintenanceIssue.objects.filter(company=self.company)


class IssueArchiveView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, RedirectView):
    permanent = True
    query_string = True
    pattern_name = "high_ui:project_details"

    def get_object(self, queryset=None):
        issue = self.get_queryset().filter(company_issue_number=self.kwargs.get("company_issue_number")).first()
        return issue

    def get_queryset(self):
        return MaintenanceIssue.objects.filter(company=self.company)

    def get_redirect_url(self, *args, **kwargs):
        issue = self.get_object()
        issue.archive()
        del kwargs["company_issue_number"]
        return super().get_redirect_url(*args, **kwargs)
