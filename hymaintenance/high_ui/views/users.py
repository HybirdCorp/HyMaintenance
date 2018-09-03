from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from customers.forms import AdminUserCreateForm
from customers.forms import MaintenanceUserModelForm
from customers.forms import MaintenanceUserProfileUpdateForm
from customers.forms import ManagerUserCreateForm
from customers.forms import ManagerUsersUpdateForm
from customers.forms import OperatorUserArchiveForm
from customers.forms import OperatorUserCreateForm
from customers.forms import OperatorUserCreateFormWithCompany
from customers.forms import OperatorUsersUpdateForm
from customers.forms import OperatorUserUnarchiveForm
from customers.forms import StaffUserProfileUpdateForm
from customers.forms import StaffUserUpdateForm
from customers.models.user import MaintenanceUser
from maintenance.forms.consumer import MaintenanceConsumerModelForm
from maintenance.forms.consumer import MaintenanceConsumersUpdateForm
from maintenance.models import MaintenanceConsumer

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany
from .base import get_context_data_dashboard_header
from .base import get_context_data_footer


class ConsumerCreateView(ViewWithCompany, IsAtLeastAllowedOperatorTestMixin, CreateView):
    form_class = MaintenanceConsumerModelForm
    template_name = "high_ui/forms/create_consumer.html"

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
    form_class = ManagerUserCreateForm
    template_name = "high_ui/forms/create_manager.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class MaintenanceUserUpdateView(TemplateView):
    def get_object(self):
        return self.get_queryset().get(id=self.kwargs.get("pk"))

    def get_password_form(self, *args, **kwargs):
        form = SetPasswordForm(*args, **kwargs)
        return form

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

    def get_profile_form(self, *args, **kwargs):
        return MaintenanceUserModelForm(*args, **kwargs)

    def get_queryset(self):
        return MaintenanceUser.objects.get_manager_users_queryset()


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


class AdminUserCreateView(IsAdminTestMixin, CreateView):
    form_class = AdminUserCreateForm
    template_name = "high_ui/forms/create_admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_data_footer())
        return context

    def get_success_url(self):
        return reverse("high_ui:admin")


class AdminUserUpdateView(IsAdminTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_admin.html"

    def get_profile_form(self, *args, **kwargs):
        return StaffUserUpdateForm(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_data_footer())
        return context

    def get_queryset(self):
        return MaintenanceUser.objects.get_admin_users_queryset()


class OperatorUserCreateView(IsAdminTestMixin, CreateView):
    form_class = OperatorUserCreateForm
    template_name = "high_ui/forms/create_operator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_data_footer())
        return context

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class OperatorUserCreateViewWithCompany(ViewWithCompany, IsAdminTestMixin, CreateView):
    form_class = OperatorUserCreateFormWithCompany
    template_name = "high_ui/forms/create_company_operator.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class OperatorUserUpdateView(IsAdminTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_operator.html"

    def get_profile_form(self, *args, **kwargs):
        return StaffUserUpdateForm(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_data_footer())
        return context

    def get_queryset(self):
        return MaintenanceUser.objects.get_operator_users_queryset()


class OperatorUserUpdateViewWithCompany(ViewWithCompany, IsAdminTestMixin, MaintenanceUserUpdateView):
    template_name = "high_ui/forms/update_company_operator.html"

    def get_profile_form(self, *args, **kwargs):
        return StaffUserUpdateForm(*args, **kwargs)

    def get_queryset(self):
        return MaintenanceUser.objects.get_active_operator_users_queryset()


class OperatorUsersUpdateViewWithCompany(ViewWithCompany, IsAdminTestMixin, FormView):
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


class OperatorUsersUpdateView(IsAdminTestMixin, TemplateView):
    template_name = "high_ui/forms/update_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
        context.update(get_context_data_footer())
        context["archive_form"] = OperatorUserArchiveForm()
        context["unarchive_form"] = OperatorUserUnarchiveForm()
        context["active_operators_number"] = MaintenanceUser.objects.get_active_operator_users_queryset().count()
        context["archived_operators_number"] = (
            MaintenanceUser.objects.get_operator_users_queryset().count() - context["active_operators_number"]
        )
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


class UserUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/forms/update_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_footer())
        return context

    def get_object(self):
        return self.request.user

    def get_password_form(self, *args, **kwargs):
        form = PasswordChangeForm(*args, **kwargs)
        # Remove the (REALLY) annoying autofocus of this field
        form.fields["old_password"].widget.attrs["autofocus"] = False
        return form

    def get_profile_form(self, is_staff, *args, **kwargs):
        if is_staff:
            return StaffUserProfileUpdateForm(*args, **kwargs)
        else:
            return MaintenanceUserProfileUpdateForm(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        profile_form = self.get_profile_form(is_staff=self.request.user.is_staff, instance=user)
        password_form = self.get_password_form(user)
        return self.render_to_response(self.get_context_data(profile_form=profile_form, password_form=password_form))

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        context = {}
        # initial state
        profile_form = self.get_profile_form(is_staff=self.request.user.is_staff, instance=user)
        password_form = self.get_password_form(user)

        data = request.POST.copy()
        form_mod = data.pop("form-mod", [None])[0]

        if form_mod == "profile":
            profile_form = self.get_profile_form(is_staff=self.request.user.is_staff, data=data, instance=user)
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
