from django import forms

from customers.models import MaintenanceUser

from .models import MaintenanceConsumer, MaintenanceIssue


# TODO: limit the "user_who_fix" choices to valid MaintenanceUsers
# TODO: similarly, limit the consumer_who_ask MaintenanceConsumer to the current company ones
class MaintenanceIssueCreateForm(forms.ModelForm):
    duration = forms.IntegerField(min_value=0, required=True)
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
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super(MaintenanceIssueCreateForm, self).__init__(*args, **kwargs)

        self.fields["consumer_who_ask"].queryset = self.company.maintenanceconsumer_set
        self.fields["user_who_fix"].choices = MaintenanceUser.objects.get_maintainers_choices()

    def clean(self):
        cleaned_data = super(MaintenanceIssueCreateForm, self).clean()

        duration = cleaned_data.get("duration")
        duration_type = cleaned_data.get("duration_type")

        if duration_type not in ["minutes", "hours"]:
            self.add_error("duration", "Invalid duration type: '%s'" % duration_type)

        if duration <= 0:
            self.add_error("duration", "Invalid duration: '%s'" % duration)

    def save(self, commit=True):
        form_data = self.cleaned_data

        self.instance.company = self.company

        number_minutes = form_data['duration']
        if form_data['duration_type'] == "hours":
            number_minutes *= 60

        self.instance.number_minutes = number_minutes
        return super(MaintenanceIssueCreateForm, self).save(commit)


class MaintenanceConsumerCreateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceConsumer
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super(MaintenanceConsumerCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.company = self.company
        return super(MaintenanceConsumerCreateForm, self).save(commit)
