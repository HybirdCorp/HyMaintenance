from django.urls import reverse
from django.views.generic import CreateView

from customers.forms.users.create_user import AdminUserCreateForm
from customers.forms.users.create_user import ManagerUserCreateForm
from customers.forms.users.create_user import OperatorUserCreateForm
from customers.forms.users.create_user import OperatorUserCreateFormWithCompany
from maintenance.forms.consumer import MaintenanceConsumerModelForm

from ..base import IsAdminTestMixin
from ..base import IsAtLeastAllowedOperatorTestMixin
from ..base import ViewWithCompany
from ..base import get_context_data_dashboard_header
from ..base import get_context_previous_page


class ConsumerCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceConsumerModelForm
    template_name = "high_ui/forms/create_consumer.html"

    def previous_page(self):
        return get_context_previous_page(self.request)["previous_page"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class ManagerUserCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = ManagerUserCreateForm
    template_name = "high_ui/forms/create_manager.html"

    def previous_page(self):
        return get_context_previous_page(self.request)["previous_page"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class OperatorUserCreateView(IsAdminTestMixin, CreateView):
    form_class = OperatorUserCreateForm
    template_name = "high_ui/forms/create_operator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def previous_page(self):
        return get_context_previous_page(self.request)["previous_page"]

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class OperatorUserCreateViewWithCompany(ViewWithCompany, IsAdminTestMixin, CreateView):
    form_class = OperatorUserCreateFormWithCompany
    template_name = "high_ui/forms/create_company_operator.html"

    def previous_page(self):
        return get_context_previous_page(self.request)["previous_page"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class AdminUserCreateView(IsAdminTestMixin, CreateView):
    form_class = AdminUserCreateForm
    template_name = "high_ui/forms/create_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    def previous_page(self):
        return get_context_previous_page(self.request)["previous_page"]

    def get_success_url(self):
        return reverse("high_ui:admin")
