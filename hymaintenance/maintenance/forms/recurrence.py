from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from ..models import MaintenanceContract


class RecurrenceContractsModelForm(forms.ModelForm):
    class Meta:
        model = MaintenanceContract
        fields = (
            "recurrence_start_date",
            "hours_to_credit",
            "has_credit_recurrence",
            "credit_recurrence",
            "recurrence_next_date",
            "id",
            "has_reset_recurrence"
        )
        widgets = {
            "id": forms.HiddenInput(attrs={"readonly": True}),
            "recurrence_next_date": forms.TextInput(attrs={"readonly": True}),
            "credit_recurrence": forms.HiddenInput(),
            "has_credit_recurrence": forms.HiddenInput(),
            "hours_to_credit": forms.TextInput(),
            "has_reset_recurrence": forms.HiddenInput(),
        }
        labels = {
            "recurrence_start_date": _("Start"),
            "credit_recurrence": _("Frequency"),
            "has_reset_recurrence": _("Reset counter")
        }

    css_class = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"readonly": True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter_name = self.instance.get_counter_name()
        if self.instance:
            self.fields['css_class'].initial = self.instance.maintenance_type.css_class

    def clean_recurrence_start_date(self):
        start_date = self.cleaned_data.get("recurrence_start_date")
        check_authorized_recurrence_start_date(start_date)
        return start_date


def check_authorized_recurrence_start_date(start_date, now_date=None):
    if now_date is None:
        now_date = now().date()
    if start_date is not None and now_date - start_date >= timedelta(weeks=52):
        raise ValidationError(
            _("Invalid Recurrence Start Date: %(value)s, the date can't be older than one year."),
            code="invalid_recurrence_start_date",
            params={"value": start_date},
        )
