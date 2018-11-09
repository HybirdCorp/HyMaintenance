from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.views.generic import TemplateView

from customers.forms.users.user_profile import MaintenanceUserProfileUpdateForm
from customers.forms.users.user_profile import StaffUserProfileUpdateForm


class UserUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "high_ui/forms/update_profile.html"

    def get_object(self):
        return self.request.user

    @staticmethod
    def get_password_form(*args, **kwargs):
        form = PasswordChangeForm(*args, **kwargs)
        # Remove the (REALLY) annoying autofocus of this field
        form.fields["old_password"].widget.attrs["autofocus"] = False
        return form

    @staticmethod
    def get_profile_form(is_staff, *args, **kwargs):
        if is_staff:
            return StaffUserProfileUpdateForm(*args, **kwargs)
        else:
            return MaintenanceUserProfileUpdateForm(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        is_staff = self.request.user.is_staff or self.request.user.is_superuser
        profile_form = self.get_profile_form(is_staff=is_staff, instance=user)
        password_form = self.get_password_form(user)
        return self.render_to_response(self.get_context_data(profile_form=profile_form, password_form=password_form))

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        context = {}
        # initial state
        is_staff = self.request.user.is_staff or self.request.user.is_superuser
        profile_form = self.get_profile_form(is_staff=is_staff, instance=user)
        password_form = self.get_password_form(user)

        data = request.POST.copy()
        form_mod = data.pop("form-mod", [None])[0]

        if form_mod == "profile":
            profile_form = self.get_profile_form(is_staff=is_staff, data=data, instance=user)
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
