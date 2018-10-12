from django import forms
from django.contrib.auth import password_validation
from django.utils.translation import ugettext_lazy as _

from ...models import MaintenanceUser


class MaintenanceUserModelForm(forms.ModelForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def fill_user(self, user):
        """Extending classes can modify the user here before it is saved.
        This default implementation does nothing, no need to call super
        """
        pass


class MaintenanceUserCreateForm(MaintenanceUserModelForm):
    error_messages = {"password_mismatch": _("The two password fields didn't match.")}
    password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        required=True,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("New password confirmation"), strip=False, required=True, widget=forms.PasswordInput
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages["password_mismatch"], code="password_mismatch")
        password_validation.validate_password(password2)
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        self.fill_user(user)

        if commit:
            user.save()
        return user


class StaffUserUpdateForm(MaintenanceUserModelForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "phone", "email")
