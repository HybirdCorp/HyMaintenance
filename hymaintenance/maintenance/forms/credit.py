from django import forms
from django.utils.timezone import now

from ..models import MaintenanceContract
from ..models import MaintenanceCredit
from ..models.credit import MaintenanceCreditChoices


class MaintenanceCreditCreateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceCredit
        fields = ("hours_number", "contract", "subject", "date")
        widgets = {"hours_number": forms.TextInput(), "contract": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)
        self.fields["hours_number"].initial = MaintenanceCreditChoices.objects.all().order_by("id").first().value
        self.fields["date"].initial = now().date()
        self.fields["contract"].queryset = MaintenanceContract.objects.filter(company=self.company)

    def save(self, commit=True):
        self.instance.company = self.company
        return super().save(commit)


class MaintenanceCreditUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceCredit
        fields = ("hours_number", "contract", "subject", "date")
        widgets = {"hours_number": forms.TextInput(), "contract": forms.HiddenInput()}
