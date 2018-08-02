from django import forms

from ..models import MaintenanceCredit


class MaintenanceCreditCreateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceCredit
        fields = ("hours_number", "contract")
        widgets = {"hours_number": forms.HiddenInput(), "contract": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        hours_number_initial = kwargs.pop("hours_number_initial")
        super().__init__(*args, **kwargs)
        self.fields["hours_number"].initial = hours_number_initial

    def save(self, commit=True):
        self.instance.company = self.company
        return super().save(commit)
