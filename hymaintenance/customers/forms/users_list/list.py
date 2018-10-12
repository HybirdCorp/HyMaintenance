from django import forms

from ...models import MaintenanceUser


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
