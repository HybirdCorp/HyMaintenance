from toolkit.forms import UsersMultipleChoiceField

from django import forms

from ...models import MaintenanceUser


class OperatorUsersListUpdateForm(forms.Form):
    users = UsersMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, queryset=None)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)
        self.fields["users"].queryset = MaintenanceUser.objects.get_active_all_types_operator_users_queryset()
        self.fields["users"].initial = self.company.managed_by.all().order_by("first_name", "last_name")

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


class ManagerUsersListUpdateForm(forms.Form):
    users = UsersMultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, queryset=None)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)
        self.fields["users"].queryset = MaintenanceUser.objects.filter(
            company=self.company, is_staff=False, is_superuser=False
        )
        self.fields["users"].initial = MaintenanceUser.objects.filter(
            company=self.company, is_staff=False, is_superuser=False, is_active=True
        ).order_by("first_name", "last_name")

    def save(self):
        for manager in self.cleaned_data["users"].filter(is_active=False):
            manager.is_active = True
            manager.save()
        managers_set = set(self.cleaned_data["users"])
        for manager in self.fields["users"].queryset.filter(is_active=True):
            if manager not in managers_set:
                manager.is_active = False
                manager.save()
