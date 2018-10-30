from ...models import MaintenanceUser
from .user_base import MaintenanceUserModelForm


class OperatorUserUpdateForm(MaintenanceUserModelForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "phone", "email")


class AdminUserUpdateForm(MaintenanceUserModelForm):
    class Meta:
        model = MaintenanceUser
        fields = ("first_name", "last_name", "phone", "email", "is_staff")
