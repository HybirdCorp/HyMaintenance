from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from customers.forms import ManagerUserModelForm
from customers.forms import ManagerUsersUpdateForm
from customers.forms import OperatorUserArchiveForm
from customers.forms import OperatorUserModelForm
from customers.forms import OperatorUserModelFormWithCompany
from customers.forms import OperatorUsersUpdateForm
from customers.forms import OperatorUserUnarchiveForm
from customers.models import Company
from customers.models.user import MaintenanceUser
from maintenance.forms.consumer import MaintenanceConsumerModelForm
from maintenance.forms.consumer import MaintenanceConsumersUpdateForm
from maintenance.models import MaintenanceConsumer
from maintenance.models import MaintenanceContract

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany


class ConsumerCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceConsumerModelForm
    template_name = "high_ui/forms/create_consumer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.company
        contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        context["contracts"] = contracts
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class ConsumerUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = MaintenanceConsumerModelForm
    template_name = "high_ui/forms/update_consumer.html"
    model = MaintenanceConsumer

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        return MaintenanceConsumer.objects.filter(company=self.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project-update_consumers", kwargs={"company_name": self.company.slug_name})


class ConsumersUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
    form_class = MaintenanceConsumersUpdateForm
    template_name = "high_ui/forms/update_consumers.html"
    success_url = "/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ManagerUserCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = ManagerUserModelForm
    template_name = "high_ui/forms/create_manager.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.company
        contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        context["contracts"] = contracts
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class ManagerUserUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = ManagerUserModelForm
    template_name = "high_ui/forms/update_manager.html"
    model = MaintenanceUser

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        return MaintenanceUser.objects.get_manager_users_queryset()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project-update_managers", kwargs={"company_name": self.company.slug_name})


class ManagerUsersUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
    form_class = ManagerUsersUpdateForm
    template_name = "high_ui/forms/update_managers.html"
    success_url = "/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUserCreateViewWithCompany(ViewWithCompany, IsAdminTestMixin, CreateView):
    form_class = OperatorUserModelFormWithCompany
    template_name = "high_ui/forms/create_operator.html"

    # TMP: Technically, only the template needs the Company right now, so don't send it to the form init.
    # This is done until we have the concept of "maintenance providers" or "projects" which this view/form
    # will need to link the MaintenanceUser to this Company as the "maintainer"
    # Until then, the view/form have the company but the MaintenanceUser created will not use it

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["company"] = self.company
        contracts = MaintenanceContract.objects.filter(company=self.company, disabled=False)
        context["contracts"] = contracts
        return context

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class OperatorUserUpdateView(IsAdminTestMixin, UpdateView):
    form_class = OperatorUserModelForm
    template_name = "high_ui/forms/update_operator.html"
    model = MaintenanceUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintainers"] = MaintenanceUser.objects.get_active_operator_users_queryset()
        context["companies"] = Company.objects.all()
        return context

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        return MaintenanceUser.objects.get_active_operator_users_queryset()

    def get_success_url(self):
        return reverse("high_ui:update_operators")


class OperatorUserUpdateViewWithCompany(ViewWithCompany, OperatorUserUpdateView):
    form_class = OperatorUserModelFormWithCompany
    template_name = "high_ui/forms/update_company_operator.html"
    model = MaintenanceUser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project-update_operators", kwargs={"company_name": self.company.slug_name})


class OperatorUsersUpdateViewWithCompany(ViewWithCompany, IsAdminTestMixin, FormView):
    form_class = OperatorUsersUpdateForm
    template_name = "high_ui/forms/update_company_operators.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operators"] = MaintenanceUser.objects.get_active_operator_users_queryset()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersUpdateView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/forms/update_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_operators = MaintenanceUser.objects.get_active_operator_users_queryset()
        context["maintainers"] = active_operators
        context["archive_form"] = OperatorUserArchiveForm()
        context["unarchive_form"] = OperatorUserUnarchiveForm()
        operators_number = MaintenanceUser.objects.get_operator_users_queryset().count()
        context["active_operators_number"] = active_operators.count()
        context["archived_operators_number"] = operators_number - active_operators.count()
        context["companies"] = Company.objects.all()
        return context


class OperatorUsersArchiveView(IsAdminTestMixin, FormView):
    form_class = OperatorUserArchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersUnarchiveView(IsAdminTestMixin, FormView):
    form_class = OperatorUserUnarchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
