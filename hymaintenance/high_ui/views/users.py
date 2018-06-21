from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from customers.forms import MaintenanceUserProfilUpdateForm
from customers.forms import ManagerUserModelForm
from customers.forms import ManagerUsersUpdateForm
from customers.forms import OperatorUserArchiveForm
from customers.forms import OperatorUserModelForm
from customers.forms import OperatorUserModelFormWithCompany
from customers.forms import OperatorUsersUpdateForm
from customers.forms import OperatorUserUnarchiveForm
from customers.models.user import MaintenanceUser
from maintenance.forms.consumer import MaintenanceConsumerModelForm
from maintenance.forms.consumer import MaintenanceConsumersUpdateForm
from maintenance.models import MaintenanceConsumer

from .base import IsAdminTestMixin
from .base import IsAtLeastAllowedOperatorTestMixin
from .base import ViewWithCompany
from .base import get_context_data_dashboard_header


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
    form_class = ManagerUserModelForm
    template_name = "high_ui/forms/create_manager.html"

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.company
        return kwargs

    def get_success_url(self):
        return reverse("high_ui:dashboard")


class OperatorUserUpdateView(IsAdminTestMixin, UpdateView):
    form_class = OperatorUserModelForm
    template_name = "high_ui/forms/update_operator.html"
    model = MaintenanceUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_context_data_dashboard_header(self.user))
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
    template_name = "high_ui/forms/update_user.html"
    success_url = reverse_lazy("high_ui:dashboard")

    def get_object(self):
        return self.request.user

    def get_password_form(self, *args, **kwargs):
        form = PasswordChangeForm(*args, **kwargs)
        form.fields['old_password'].widget.attrs['autofocus'] = False
        return form

    def get_profile_form(self, *args, **kwargs):
        return MaintenanceUserProfilUpdateForm(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        profile_form = MaintenanceUserProfilUpdateForm(instance=user)
        password_form = self.get_password_form(user)
        return self.render_to_response(
            self.get_context_data(profile_form=profile_form,
                                  password_form=password_form))

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        context = {}
        # initial state
        profile_form = self.get_profile_form(instance=user)
        password_form = self.get_password_form(user)

        data = request.POST.copy()
        form_mod = data.pop('form-mod', [None])[0]

        if form_mod == 'profile':
            profile_form = self.get_profile_form(
                data=data, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                context['profile_form_success'] = True

        elif form_mod == 'password':
            password_form = self.get_password_form(user, data=data)
            if password_form.is_valid():
                password_form.save()
                context['password_form_success'] = True

        return self.render_to_response(
            self.get_context_data(profile_form=profile_form,
                                  password_form=password_form, **context))
