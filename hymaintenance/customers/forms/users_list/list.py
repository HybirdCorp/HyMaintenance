from django import forms

from ...models import MaintenanceUser


class OperatorUsersListArchiveForm(forms.Form):
    active_users = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=True),
    )

    def save(self):
        for user in self.cleaned_data["active_users"]:
            user.is_active = False
            user.save()


class OperatorUsersListUnarchiveForm(forms.Form):
    inactive_users = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=False),
    )

    def save(self):
        for user in self.cleaned_data["inactive_users"]:
            user.is_active = True
            user.save()


class AdminUsersListArchiveForm(forms.Form):
    active_users = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_admin_users_queryset().filter(is_active=True),
    )

    def save(self):
        for user in self.cleaned_data["active_users"]:
            user.is_active = False
            user.save()


class AdminUsersListUnarchiveForm(forms.Form):
    inactive_users = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_admin_users_queryset().filter(is_active=False),
    )

    def save(self):
        for user in self.cleaned_data["inactive_users"]:
            user.is_active = True
            user.save()
