from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from toolkit.forms import UsersMultipleChoiceField

from .models import Company
from .models import MaintenanceUser


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "maintenance_contact")


class MaintenanceUserModelForm(forms.ModelForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "email", "password")
        widgets = {"password": forms.PasswordInput()}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        self.fill_user(user)

        if commit:
            user.save()
        return user

    def fill_user(self, user):
        """Extending classes can modify the user here before it is saved.
        This default implementation does nothing, no need to call super
        """
        pass


class ManagerUserModelForm(MaintenanceUserModelForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)

    def fill_user(self, user):
        user.company = self.company


class ManagerUsersUpdateForm(forms.Form):
    users = UsersMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, queryset=None)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)
        self.fields["users"].queryset = MaintenanceUser.objects.filter(company=self.company, is_staff=False)
        self.fields["users"].initial = MaintenanceUser.objects.filter(
            company=self.company, is_staff=False, is_active=True
        )

    def save(self):
        for manager in self.cleaned_data["users"].filter(is_active=False):
            manager.is_active = True
            manager.save()
        managers_set = set(self.cleaned_data["users"])
        for manager in self.fields["users"].queryset.filter(is_active=True):
            if manager not in managers_set:
                manager.is_active = False
                manager.save()


class OperatorUserModelForm(MaintenanceUserModelForm):
    def fill_user(self, user):
        user.is_staff = True


class OperatorUserModelFormWithCompany(OperatorUserModelForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.operator_for.add(self.company)
        return user


class OperatorUsersUpdateForm(forms.Form):
    users = UsersMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, queryset=None)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)
        self.fields["users"].queryset = MaintenanceUser.objects.get_active_operator_users_queryset()
        self.fields["users"].initial = self.company.managed_by.all()

    def save(self):
        for operator in self.cleaned_data["users"]:
            if operator not in self.fields["users"].initial:
                operator.operator_for.add(self.company)
                operator.save()
        operators_set = set(self.cleaned_data["users"])
        for operator in self.fields["users"].queryset:
            if operator not in operators_set and operator in self.fields["users"].initial:
                operator.operator_for.remove(self.company)
                operator.save()


class OperatorUserArchiveForm(forms.Form):
    active_operators = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=True),
    )

    def save(self):
        for operator in self.cleaned_data["active_operators"]:
            operator.is_active = False
            operator.save()


class OperatorUserUnarchiveForm(forms.Form):
    inactive_operators = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=False),
    )

    def save(self):
        for operator in self.cleaned_data["inactive_operators"]:
            operator.is_active = True
            operator.save()


class MaintenanceUserProfileUpdateForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label="Confirmer le mot de passe", strip=False, widget=forms.PasswordInput, required=True
    )

    class Meta:
        model = MaintenanceUser
        fields = ("confirm_password", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def clean_confirm_password(self):
        password = self.cleaned_data["confirm_password"]
        if not self.instance.check_password(password):
            raise ValidationError(_("Invalid password."))
