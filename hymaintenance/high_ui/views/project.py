from datetime import datetime, timedelta

from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, FormView

from customers.models import Company, MaintenanceUser
from maintenance.forms.project import ProjectCreateForm, ProjectUpdateForm
from maintenance.models import MaintenanceContract, MaintenanceIssue, MaintenanceType

from .base import IsAdminTestMixin, IsAtLeastAllowedManagerTestMixin, ViewWithCompany


class ProjectCreateView(IsAdminTestMixin, FormView):
    form_class = ProjectCreateForm
    template_name = "high_ui/forms/create_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        user = self.request.user
        if not user.is_staff:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': Company._meta.verbose_name})
        context = super().get_context_data(**kwargs)
        context["maintenance_types"] = MaintenanceType.objects.order_by("id")
        context["companies"] = Company.objects.all()
        context["maintainers"] = MaintenanceUser.objects.get_operator_users_queryset()
        return context

    def form_valid(self, form):
        form.create_company_and_contracts()
        return super().form_valid(form)


class ProjectUpdateView(IsAdminTestMixin, ViewWithCompany, FormView):
    form_class = ProjectUpdateForm
    template_name = "high_ui/forms/update_project.html"
    success_url = "/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.update_company_and_contracts()
        return super().form_valid(form)


class ProjectDetailsView(ViewWithCompany, IsAtLeastAllowedManagerTestMixin, DetailView):
    template_name = 'high_ui/company_details.html'
    model = Company
    slug_url_kwarg = "company_name"
    slug_field = "slug_name"

    def get_maintenance_contracts(self):
        user = self.request.user
        if user.is_staff:
            contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        else:
            contracts = MaintenanceContract.objects.filter(company=self.company, visible=True, disabled=False)
        return contracts

    def get_maintenance_issues(self, month):
        user = self.request.user
        if user.is_staff:
            issues = MaintenanceIssue.objects.filter(company=self.company,
                                                     date__month=month.month,
                                                     date__year=month.year
                                                     ).order_by("-date")
        else:
            maintenance_type_ids = MaintenanceContract.objects.values_list('maintenance_type').filter(visible=True, company_id=self.company, disabled=False)
            issues = MaintenanceIssue.objects.filter(maintenance_type__in=maintenance_type_ids,
                                                     company_id=self.company,
                                                     date__month=month.month,
                                                     date__year=month.year
                                                     ).order_by("-date")
        return issues

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailsView, self).get_context_data(**kwargs)
        self.company = self.object
        contracts = self.get_maintenance_contracts()
        now = datetime.now()
        last_month = now - timedelta(days=(now.day + 1))
        months = [now, last_month]
        for i in range(4):
            last_month = last_month - timedelta(days=31)
            months.append(last_month)

        # months = [now, last_month, two_month_ago]
        activities = []
        for month in months:
            info_contract = []
            for contract in contracts:
                info_contract.append((contract, contract.get_number_consumed_minutes_in_month(month),
                                      contract.get_number_credited_hours_in_month(month)))
            activities.append((month, info_contract))

        history = []
        for month in months:
            info_contract = []
            # info_issues = []
            for contract in contracts:
                info_contract.append((contract, contract.get_number_consumed_minutes_in_month(month),
                                      contract.get_number_credited_hours_in_month(month)))

            issues = self.get_maintenance_issues(month)
            info_issues = list(issues)
            history.append((month, info_contract, info_issues))

        context["contracts"] = contracts
        context["activities"] = activities
        context["history"] = history

        # TMP: when renaming the model to Company, this following line will be useless
        context["company"] = context["object"]

        return context
