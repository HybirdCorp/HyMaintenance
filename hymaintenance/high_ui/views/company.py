from datetime import datetime, timedelta

from django.views.generic import DetailView

from customers.models import Company
from maintenance.models import MaintenanceContract, MaintenanceIssue

from .base import LoginRequiredMixin


class CompanyDetailView(LoginRequiredMixin, DetailView):
    template_name = 'high_ui/company_details.html'
    model = Company
    pk_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return user.operator_for.order_by('id')
        return Company.objects.filter(pk=user.company.pk)

    def get_maintenance_contracts(self, company):
        user = self.request.user
        if user.is_staff:
            contracts = MaintenanceContract.objects.filter(company=company, disabled=False)
        else:
            contracts = MaintenanceContract.objects.filter(company=company, visible=True, disabled=False)
        return contracts

    def get_maintenance_issues(self, company, month):
        user = self.request.user
        if user.is_staff:
            issues = MaintenanceIssue.objects.filter(company=company,
                                                     date__month=month.month,
                                                     date__year=month.year
                                                     ).order_by("-date")
        else:
            maintenance_type_ids = MaintenanceContract.objects.values_list('maintenance_type').filter(visible=True, company_id=company, disabled=False)
            issues = MaintenanceIssue.objects.filter(maintenance_type__in=maintenance_type_ids,
                                                     company_id=company,
                                                     date__month=month.month,
                                                     date__year=month.year
                                                     ).order_by("-date")
        return issues

    def get_context_data(self, **kwargs):
        context = super(CompanyDetailView, self).get_context_data(**kwargs)
        contracts = self.get_maintenance_contracts(self.object)
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

            issues = self.get_maintenance_issues(self.object, month)
            info_issues = list(issues)
            history.append((month, info_contract, info_issues))

        context["contracts"] = contracts
        context["activities"] = activities
        context["history"] = history

        # TMP: when renaming the model to Company, this following line will be useless
        context["company"] = context["object"]

        return context
