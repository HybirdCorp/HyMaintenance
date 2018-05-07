from django.views.generic import FormView

from customers.models import Company, MaintenanceUser
from maintenance.forms import ProjectCreateForm, ProjectUpdateForm
from maintenance.models import IncomingChannel, MaintenanceContract, MaintenanceType

from .base import LoginRequiredMixin, ViewWithCompany


class ProjectCreateView(FormView):
    form_class = ProjectCreateForm
    template_name = "high_ui/forms/add_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintenance_types"] = MaintenanceType.objects.order_by("id")
        context["companies"] = Company.objects.all()
        context["maintainers"] = MaintenanceUser.objects.get_operator_users_queryset()
        return context

    def form_valid(self, form):
        form.create_company_and_contracts()
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, ViewWithCompany, FormView):
    form_class = ProjectUpdateForm
    template_name = "high_ui/forms/update_project.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintenance_types"] = MaintenanceType.objects.order_by("id")
        context['channels'] = IncomingChannel.objects.all()
        contracts = MaintenanceContract.objects.filter(company=self.company)
        context['contracts'] = contracts
        context['company'] = self.company
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.company
        return kwargs

    def form_valid(self, form):
        form.update_company_and_contracts()
        return super().form_valid(form)
