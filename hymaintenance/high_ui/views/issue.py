from maintenance.forms.issue import MaintenanceIssueCreateForm
from maintenance.forms.issue import MaintenanceIssueListUnarchiveForm
from maintenance.forms.issue import MaintenanceIssueUpdateForm
from maintenance.models import MaintenanceIssue

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedManagerTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany
from .base import get_context_data_dashboard_header
from .base import get_context_previous_page


class IssueCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceIssueCreateForm
    template_name = "high_ui/forms/create_issue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_previous_page(self.request))
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_previous_page(self.request))
        return context

    def get_object(self, queryset=None):
        issue = get_object_or_404(
            MaintenanceIssue, company=self.company, company_issue_number=self.kwargs.get("company_issue_number")
        )
        if issue.is_deleted:
            raise Http404("No issue matches the given query.")
        else:
            return issue

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
        issue = get_object_or_404(
            MaintenanceIssue, company=self.company, company_issue_number=self.kwargs.get("company_issue_number")
        )
        if issue.is_deleted:
            raise Http404("No issue matches the given query.")
        else:
            return issue


class IssueArchiveView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, RedirectView):
    permanent = True
    query_string = True
    pattern_name = "high_ui:project_details"

    def get_object(self, queryset=None):
        issue = get_object_or_404(
            MaintenanceIssue, company=self.company, company_issue_number=self.kwargs.get("company_issue_number")
        )
        return issue

    def get_redirect_url(self, *args, **kwargs):
        issue = self.get_object()
        issue.archive()
        del kwargs["company_issue_number"]
        return super().get_redirect_url(*args, **kwargs)


class IssueListUnarchiveView(ViewWithCompany, IsAdminTestMixin, FormView):
    form_class = MaintenanceIssueListUnarchiveForm
    template_name = "high_ui/forms/unarchive_issues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("high_ui:admin")
