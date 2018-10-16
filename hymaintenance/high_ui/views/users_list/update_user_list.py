from django.views.generic import FormView
from django.views.generic import TemplateView

from customers.forms.users_list.list import OperatorUserArchiveForm
from customers.forms.users_list.list import OperatorUserUnarchiveForm
from customers.forms.users_list.list_by_company import ManagerUsersUpdateForm
from customers.forms.users_list.list_by_company import OperatorUsersUpdateForm
from customers.models.user import MaintenanceUser
from maintenance.forms.consumer import MaintenanceConsumersUpdateForm

from ..base import IsAdminTestMixin
from ..base import IsAtLeastAllowedOperatorTestMixin
from ..base import ViewWithCompany
from ..base import get_context_data_dashboard_header


class ConsumersListUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
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


class ManagerUsersListUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
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


class OperatorUsersListUpdateViewWithCompany(ViewWithCompany, IsAdminTestMixin, FormView):
    form_class = OperatorUsersUpdateForm
    template_name = "high_ui/forms/update_company_operators.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["operators_number"] = MaintenanceUser.objects.get_active_operator_users_queryset().count()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersListUpdateView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/forms/update_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context["archive_form"] = OperatorUserArchiveForm()
        context["unarchive_form"] = OperatorUserUnarchiveForm()
        context["active_operators_number"] = MaintenanceUser.objects.get_active_operator_users_queryset().count()
        context["archived_operators_number"] = (
            MaintenanceUser.objects.get_operator_users_queryset().count() - context["active_operators_number"]
        )
        return context


class OperatorUsersListArchiveView(IsAdminTestMixin, FormView):
    form_class = OperatorUserArchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersListUnarchiveView(IsAdminTestMixin, FormView):
    form_class = OperatorUserUnarchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
