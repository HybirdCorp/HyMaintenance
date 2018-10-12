from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from ...models import MaintenanceUser
from .user_base import MaintenanceUserModelForm


class MaintenanceUserProfileUpdateForm(MaintenanceUserModelForm):
    confirm_password = forms.CharField(
        label=_("Confirm password"), strip=False, widget=forms.PasswordInput, required=True
    )

    class Meta:
        model = MaintenanceUser
        fields = ("confirm_password", "first_name", "last_name", "email")

    def clean_confirm_password(self):
        password = self.cleaned_data["confirm_password"]
        if not self.instance.check_password(password):
            raise ValidationError(_("Invalid password."))


class StaffUserProfileUpdateForm(MaintenanceUserProfileUpdateForm):
    confirm_password = forms.CharField(
        label=_("Confirm password"), strip=False, widget=forms.PasswordInput, required=True
    )

    class Meta:
        model = MaintenanceUser
        fields = ("confirm_password", "first_name", "last_name", "email", "phone")
