from customers.forms.users.update_user import AdminUserUpdateForm
from customers.forms.users.update_user import OperatorUserUpdateForm
from customers.forms.users.user_base import MaintenanceUserModelForm
from customers.models.user import MaintenanceUser
from maintenance.forms.consumer import MaintenanceConsumerModelForm
from maintenance.models import MaintenanceConsumer

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from ..base import IsAdminTestMixin
from ..base import IsAtLeastAllowedOperatorTestMixin
from ..base import ViewWithCompany
from ..base import get_context_data_dashboard_header
from ..base import get_context_previous_page


class ConsumerUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, UpdateView):
    form_class = MaintenanceConsumerModelForm
    template_name = "high_ui/forms/update_consumer.html"
    model = MaintenanceConsumer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_previous_page(self.request))
        return context

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    def get_queryset(self):
        return MaintenanceConsumer.objects.filter(company=self.company)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:project-update_consumers", kwargs={"company_name": self.company.slug_name})


class MaintenanceUserUpdateView(TemplateView):
    def get_object(self):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    @staticmethod
    def get_password_form(*args, **kwargs):
        form = SetPasswordForm(*args, **kwargs)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_previous_page(self.request))
        return context

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        profile_form = self.get_profile_form(instance=user)
        password_form = self.get_password_form(user)
        return self.render_to_response(self.get_context_data(profile_form=profile_form, password_form=password_form))

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        context = {}
        # initial state
        profile_form = self.get_profile_form(instance=user)
        password_form = self.get_password_form(user)

        data = request.POST.copy()
        form_mod = data.pop("form-mod", [None])[0]

        if form_mod == "profile":
            profile_form = self.get_profile_form(data=data, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                context["profile_form_success"] = True

        elif form_mod == "password":
            password_form = self.get_password_form(user, data=data)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                context["password_form_success"] = True

        else:
            raise SuspiciousOperation

        return self.render_to_response(
            self.get_context_data(profile_form=profile_form, password_form=password_form, **context)
        )


class ManagerUserUpdateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_manager.html"

    @staticmethod
    def get_profile_form(*args, **kwargs):
        return MaintenanceUserModelForm(*args, **kwargs)

    @staticmethod
    def get_queryset():
        return MaintenanceUser.objects.get_manager_users_queryset()


class OperatorUserUpdateView(IsAdminTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_operator.html"

    @staticmethod
    def get_profile_form(*args, **kwargs):
        return OperatorUserUpdateForm(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    @staticmethod
    def get_queryset():
        return MaintenanceUser.objects.get_operator_users_queryset()


class OperatorUserUpdateViewWithCompany(ViewWithCompany, IsAdminTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_company_operator.html"

    @staticmethod
    def get_profile_form(*args, **kwargs):
        return OperatorUserUpdateForm(*args, **kwargs)

    @staticmethod
    def get_queryset():
        return MaintenanceUser.objects.get_active_all_types_operator_users_queryset()


class AdminUserUpdateView(IsAdminTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_admin.html"

    @staticmethod
    def get_profile_form(*args, **kwargs):
        return AdminUserUpdateForm(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_previous_page(self.request))
        return context

    @staticmethod
    def get_queryset():
        return MaintenanceUser.objects.get_admin_users_queryset()
