from django.views.generic import FormView
from django.views.generic import TemplateView

from customers.forms.users_list.list import AdminUsersListArchiveForm
from customers.forms.users_list.list import AdminUsersListUnarchiveForm
from customers.forms.users_list.list import OperatorUsersListArchiveForm
from customers.forms.users_list.list import OperatorUsersListUnarchiveForm
from customers.forms.users_list.list_by_company import ManagerUsersListUpdateForm
from customers.forms.users_list.list_by_company import OperatorUsersListUpdateForm
from customers.models.user import MaintenanceUser
from maintenance.forms.consumer import MaintenanceConsumersListUpdateForm

from ..base import IsAdminTestMixin
from ..base import IsAtLeastAllowedOperatorTestMixin
from ..base import ViewWithCompany
from ..base import get_context_data_dashboard_header


class ConsumersListUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, FormView):
    form_class = MaintenanceConsumersListUpdateForm
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
    form_class = ManagerUsersListUpdateForm
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
    form_class = OperatorUsersListUpdateForm
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
        context["archive_form"] = OperatorUsersListArchiveForm()
        context["unarchive_form"] = OperatorUsersListUnarchiveForm()
        context["active_users_number"] = MaintenanceUser.objects.get_active_operator_users_queryset().count()
        context["archived_users_number"] = (
            MaintenanceUser.objects.get_operator_users_queryset().count() - context["active_users_number"]
        )
        return context


class OperatorUsersListArchiveView(IsAdminTestMixin, FormView):
    form_class = OperatorUsersListArchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class OperatorUsersListUnarchiveView(IsAdminTestMixin, FormView):
    form_class = OperatorUsersListUnarchiveForm
    success_url = "/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AdminUsersListUpdateView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/forms/update_admins.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context["archive_form"] = AdminUsersListArchiveForm()
        context["unarchive_form"] = AdminUsersListUnarchiveForm()
        context["active_users_number"] = MaintenanceUser.objects.get_active_admin_users_queryset().count()
        context["archived_users_number"] = (
            MaintenanceUser.objects.get_admin_users_queryset().count() - context["active_users_number"]
        )
        return context


class AdminUsersListArchiveView(IsAdminTestMixin, FormView):
    form_class = AdminUsersListArchiveForm
    success_url = "/high_ui/admin/"  # TMP

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AdminUsersListUnarchiveView(IsAdminTestMixin, FormView):
    form_class = AdminUsersListUnarchiveForm
    success_url = "/high_ui/admin/"  # TMP

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
