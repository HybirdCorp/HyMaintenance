
from ...models import MaintenanceUser
from .user_base import MaintenanceUserCreateForm


class ManagerUserCreateForm(MaintenanceUserCreateForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)

    def fill_user(self, user):
        user.company = self.company


class AdminUserCreateForm(MaintenanceUserCreateForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "phone", "email")

    def fill_user(self, user):
        user.is_staff = True
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
