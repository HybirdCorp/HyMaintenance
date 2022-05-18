
from django import forms

from ..models.other_models import MaintenanceType


class MaintenanceTypeNameUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceType
        fields = ("name", "id")

    form_label = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"readonly": True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['form_label'].initial = instance.form_label
