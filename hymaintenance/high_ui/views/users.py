from django.http import Http404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
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
from customers.models.user import get_companies_of_operator
from maintenance.forms.consumer import MaintenanceConsumerModelForm
from maintenance.forms.consumer import MaintenanceConsumersUpdateForm
from maintenance.models import MaintenanceConsumer

from .base import CreateViewWithCompany
from .base import LoginRequiredMixin
from .base import ViewWithCompany


class ConsumerCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = MaintenanceConsumerModelForm
    template_name = "high_ui/forms/create_consumer.html"


class ConsumerUpdateView(LoginRequiredMixin, ViewWithCompany, UpdateView):
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


class ConsumersUpdateView(LoginRequiredMixin, ViewWithCompany, FormView):
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


class ManagerUserCreateView(LoginRequiredMixin, CreateViewWithCompany):
    form_class = ManagerUserModelForm
    template_name = "high_ui/forms/create_manager.html"


class ManagerUserUpdateView(LoginRequiredMixin, ViewWithCompany, UpdateView):
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


class ManagerUsersUpdateView(LoginRequiredMixin, ViewWithCompany, FormView):
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


class OperatorUserCreateViewWithCompany(LoginRequiredMixin, CreateViewWithCompany):
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


class OperatorUserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = OperatorUserModelForm
    template_name = "high_ui/forms/update_operator.html"
    model = MaintenanceUser

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


class OperatorUsersUpdateViewWithCompany(LoginRequiredMixin, ViewWithCompany, FormView):
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


class OperatorUsersUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/forms/update_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["maintainers"] = MaintenanceUser.objects.get_operator_users_queryset()
        context["archive_form"] = OperatorUserArchiveForm()
        context["unarchive_form"] = OperatorUserUnarchiveForm()
        context["active_operators_number"] = context["maintainers"].filter(is_active=True).count()
        context["archived_operators_number"] = context["maintainers"].filter(is_active=False).count()
        return context

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            raise Http404(
                _("No %(verbose_name)s found matching the query") % {"verbose_name": Company._meta.verbose_name}
            )
        context = self.get_context_data(**kwargs)
        context["companies"] = get_companies_of_operator(user)

        return self.render_to_response(context)


class OperatorUsersArchiveView(LoginRequiredMixin, FormView):
    form_class = OperatorUserArchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersUnarchiveView(LoginRequiredMixin, FormView):
    form_class = OperatorUserUnarchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
