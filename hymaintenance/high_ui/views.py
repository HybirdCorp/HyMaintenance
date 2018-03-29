from datetime import datetime, timedelta

from django.contrib.auth import decorators
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView, FormView, TemplateView, UpdateView

from customers.forms import CompanyCreateForm, MaintenanceManagerCreateForm, MaintenanceUserCreateForm
from customers.models import Company, MaintenanceUser
from maintenance.forms import MaintenanceConsumerCreateForm, MaintenanceIssueCreateForm, MaintenanceIssueUpdateForm, ProjectCreateForm
from maintenance.models import IncomingChannel, MaintenanceContract, MaintenanceIssue, MaintenanceType


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return decorators.login_required(view)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'high_ui/home_for_users.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.company is None:
            context = self.get_context_data(**kwargs)
            context["companies"] = Company.objects.all().prefetch_related("maintenanceuser_set")

            # TODO prefetch the Company relations in one query for all companies:
            # 1) Company to its MaintenanceConsumers
            # 2) Company to its MaintenanceUsers
            # 3) in the future, Company to its "maintenance providers" (right now MaintenanceUsers where company = null)

            # TODO: this should be the maintainers of the current "maintenance provider" company
            context["maintainers"] = MaintenanceUser.objects.get_maintainers_queryset()

            return self.render_to_response(context)

        return redirect(user.company.get_absolute_url())


class CompanyDetailView(LoginRequiredMixin, DetailView):
    template_name = 'high_ui/company_details.html'
    model = Company
    pk_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Company.objects.filter(pk=user.company.pk)
        return Company.objects.all()

    def get_maintenance_contracts(self, company):
        user = self.request.user
        if user.company:
            contracts = MaintenanceContract.objects.filter(company=company, visible=True)
        else:
            contracts = MaintenanceContract.objects.filter(company=company)
        return contracts

    def get_maintenance_issues(self, company, month):
        user = self.request.user
        if user.company:
            maintenance_type_ids = MaintenanceContract.objects.values_list('maintenance_type').filter(visible=True, company_id=company)
            issues = MaintenanceIssue.objects.filter(maintenance_type__in=maintenance_type_ids,
                                                     company_id=company,
                                                     date__month=month.month,
                                                     date__year=month.year
                                                     ).order_by("-date")
        else:
            issues = MaintenanceIssue.objects.filter(company=company,
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


class IssueDetailView(LoginRequiredMixin, DetailView):
    template_name = 'high_ui/issue_details.html'
    model = MaintenanceIssue
    pk_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return MaintenanceIssue.objects.filter(company_id=user.company.pk)
        return MaintenanceIssue.objects.all()


# DEPRECATED use CreateProject instead
class CreateCompanyView(LoginRequiredMixin, CreateView):
    form_class = CompanyCreateForm
    template_name = "high_ui/forms/add_company.html"

    def get_context_data(self, **kwargs):
        context = super(CreateCompanyView, self).get_context_data(**kwargs)
        # TMP: companies should be linked to the current "maintenance provider"
        context['companies_count'] = Company.objects.all().count()
        context["companies"] = Company.objects.all().prefetch_related("maintenanceuser_set")
        context["maintainers"] = MaintenanceUser.objects.get_maintainers_queryset()
        return context


class CreateViewWithCompany(CreateView):
    pk_url_kwarg = "company_id"

    def dispatch(self, request, *args, **kwargs):
        self.company = self.get_company()
        return super(CreateViewWithCompany, self).dispatch(request, *args, **kwargs)

    def get_company(self):
        try:
            company = Company.objects.get(pk=self.kwargs.get(self.pk_url_kwarg))
        except Company.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': Company._meta.verbose_name})
        return company

    def get_form_kwargs(self):
        kwargs = super(CreateViewWithCompany, self).get_form_kwargs()
        kwargs['company'] = self.company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateViewWithCompany, self).get_context_data(**kwargs)
        context['company'] = self.company
        contracts = MaintenanceContract.objects.filter(company=self.company)
        context['contracts'] = contracts
        return context

    def get_success_url(self):
        return self.company.get_absolute_url()


class IssueCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceIssueCreateForm
    template_name = "high_ui/forms/add_issue.html"

    def get_context_data(self, **kwargs):
        context = super(IssueCreateView, self).get_context_data(**kwargs)
        context['channels'] = IncomingChannel.objects.all()
        return context


class UpdateIssueView(LoginRequiredMixin, UpdateView):
    form_class = MaintenanceIssueUpdateForm
    template_name = "high_ui/forms/update_issue.html"
    model = MaintenanceIssue

    def get_context_data(self, **kwargs):
        context = super(UpdateIssueView, self).get_context_data(**kwargs)
        context['channels'] = IncomingChannel.objects.all()

        contracts = MaintenanceContract.objects.filter(company=self.object.company_id)
        context['contracts'] = contracts
        return context

    def get_success_url(self):
        return reverse('high_ui:issue-details', kwargs={'pk': self.object.id})


class CreateConsumerView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceConsumerCreateForm
    template_name = "high_ui/forms/add_consumer.html"


class CreateManagerView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceManagerCreateForm
    template_name = "high_ui/forms/add_user.html"

    def get_context_data(self, **kwargs):
        context = super(CreateManagerView, self).get_context_data(**kwargs)
        context['form_label'] = "Nouveau manager"
        context['form_submit_label'] = "Ajouter ce manager"
        return context


class CreateMaintainerView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceUserCreateForm
    template_name = "high_ui/forms/add_user.html"

    # TMP: Technically, only the template needs the Company right now, so don't send it to the form init.
    # This is done until we have the concept of "maintenance providers" or "projects" which this view/form
    # will need to link the MaintenanceUser to this Company as the "maintainer"
    # Until then, the view/form have the company but the MaintenanceUser created will not use it
    def get_form_kwargs(self):
        return super(CreateView, self).get_form_kwargs()

    def get_success_url(self):
        return reverse('high_ui:home')

    def get_context_data(self, **kwargs):
        context = super(CreateMaintainerView, self).get_context_data(**kwargs)
        context['form_label'] = "Nouvel intervenant"
        context['form_submit_label'] = "Ajouter cet intervenant"
        return context


class CreateProjectView(FormView):
    form_class = ProjectCreateForm
    template_name = "high_ui/forms/add_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super(CreateProjectView, self).get_context_data(**kwargs)
        context["maintenance_types"] = MaintenanceType.objects.all()
        context["companies"] = Company.objects.all().prefetch_related("maintenanceuser_set")
        context["maintainers"] = MaintenanceUser.objects.get_maintainers_queryset()
        return context

    def form_valid(self, form):
        form.save_company_and_contracts()
        return super().form_valid(form)
