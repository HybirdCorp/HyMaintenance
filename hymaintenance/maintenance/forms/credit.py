from django import forms

from ..models import MaintenanceContract
from ..models import MaintenanceCredit


class MaintenanceCreditCreateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceCredit
        fields = ("hours_number", "contract")
        widgets = {"hours_number": forms.TextInput(), "contract": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        hours_number_initial = kwargs.pop("hours_number_initial")
        super().__init__(*args, **kwargs)
        self.fields["hours_number"].initial = hours_number_initial
        self.fields["contract"].queryset = MaintenanceContract.objects.filter(company=self.company)

    def save(self, commit=True):
        self.instance.company = self.company
        return super().save(commit)


class MaintenanceCreditUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceCredit
        fields = ("hours_number", "contract")
        widgets = {"hours_number": forms.TextInput(), "contract": forms.HiddenInput()}
