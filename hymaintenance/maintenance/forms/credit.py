from django import forms

from ..models import MaintenanceCredit


class MaintenanceCreditCreateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceCredit
        fields = ("hours_number", "maintenance_type")

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.company = self.company
        return super().save(commit)
