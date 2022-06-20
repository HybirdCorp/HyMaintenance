from maintenance.models import MaintenanceConsumer

from django import forms

from ...models import MaintenanceUser
from .user_base import MaintenanceUserCreateForm


class ManagerUserCreateForm(MaintenanceUserCreateForm):
    create_consumer = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)

    def fill_user(self, user):
        user.company = self.company

    def save(self, commit=True):
        form_data = self.cleaned_data

        user = super().save(commit=commit)
        if "create_consumer" in form_data and form_data["create_consumer"]:
            consumer = MaintenanceConsumer(company=user.company, name=user.get_full_name())
            consumer.save()

        return user


class AdminUserCreateForm(MaintenanceUserCreateForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "phone", "email", "is_staff")

    def fill_user(self, user):
        user.is_superuser = True


class OperatorUserCreateForm(MaintenanceUserCreateForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "phone", "email")

    def fill_user(self, user):
        user.is_staff = True


class OperatorUserCreateFormWithCompany(OperatorUserCreateForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.operator_for.add(self.company)
        return user
