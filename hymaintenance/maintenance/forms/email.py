from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import MaintenanceContract


class EmailAlertUpdateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceContract
        fields = (
            "email_alert",
            "credited_hours_min",
            "recipient",
            "id",
        )
        widgets = {
            "email_alert": forms.HiddenInput(),
            "credited_hours_min": forms.TextInput(),
            "id": forms.HiddenInput(attrs={"readonly": True}),
        }
        labels = {"credited_hours_min": _("Hour threshold"), "recipient": _("To contact")}

    css_class = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"readonly": True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['css_class'].initial = self.instance.maintenance_type.css_class
