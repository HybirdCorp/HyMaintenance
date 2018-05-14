from django import forms
from django.forms.widgets import ClearableFileInput

from customers.models import Company

from ..models import MaintenanceIssue


def duration_in_minutes(duration, duration_type):
    if duration_type == "hours":
        duration *= 60
    return duration


class AttachmentInput(ClearableFileInput):
    template_name = 'maintenance/forms/widgets/attachment.html'


class MaintenanceIssueCreateForm(forms.ModelForm):
    duration = forms.IntegerField(min_value=1, required=True, widget=forms.TextInput())
    duration_type = forms.CharField(widget=forms.HiddenInput(), required=True)

    class Meta:
        model = MaintenanceIssue
        fields = MaintenanceIssue.fields_for_form + ('duration', 'duration_type')
        widgets = {
            # 'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            # 'resolution_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            # 'shipping_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'answer': forms.Textarea(attrs={'rows': 4}),
            'incoming_channel': forms.HiddenInput(),
            'maintenance_type': forms.HiddenInput(),
            'context_description_file': AttachmentInput,
            'resolution_description_file': AttachmentInput,
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super(MaintenanceIssueCreateForm, self).__init__(*args, **kwargs)

        self.fields["consumer_who_ask"].queryset = self.company.maintenanceconsumer_set
        self.fields["user_who_fix"].choices = self.company.get_operators_choices()
        self.fields["context_description_file"].required = False
        self.fields["resolution_description_file"].required = False

    def clean_duration_type(self):
        duration_type = self.cleaned_data['duration_type']
        if duration_type not in ["minutes", "hours"]:
            self.add_error("duration", "Invalid duration type: '%s'" % duration_type)
        return duration_type

    def save(self, commit=True):
        form_data = self.cleaned_data

        self.instance.company = self.company

        number_minutes = duration_in_minutes(form_data['duration'], form_data['duration_type'])
        self.instance.number_minutes = number_minutes

        return super().save(commit)


class MaintenanceIssueUpdateForm(MaintenanceIssueCreateForm):
    def __init__(self, *args, **kwargs):
        super(MaintenanceIssueCreateForm, self).__init__(*args, **kwargs)
        self.company = Company.objects.get(id=self.instance.company_id)

        self.fields["consumer_who_ask"].queryset = self.company.maintenanceconsumer_set
        self.fields["user_who_fix"].choices = self.company.get_operators_choices()
        self.fields["duration_type"].initial = "minutes"
        self.fields["duration"].initial = self.instance.number_minutes
        self.fields["context_description_file"].required = False
        self.fields["resolution_description_file"].required = False