from django import forms
from django.utils.translation import ugettext_lazy as _

from customers.models import Company, MaintenanceUser

from .models import MaintenanceConsumer, MaintenanceContract, MaintenanceIssue, MaintenanceType


INACTIF_CONTRACT_INPUT = -1


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


class ProjectCreateForm(forms.Form):
    company_name = forms.CharField(max_length=255, required=True)
    contract1_visible = forms.IntegerField(widget=forms.HiddenInput())
    contract2_visible = forms.IntegerField(widget=forms.HiddenInput())
    contract3_visible = forms.IntegerField(widget=forms.HiddenInput())
    contract1_total_type = forms.IntegerField(widget=forms.HiddenInput())
    contract2_total_type = forms.IntegerField(widget=forms.HiddenInput())
    contract3_total_type = forms.IntegerField(widget=forms.HiddenInput())
    contract1_number_hours = forms.IntegerField(min_value=0, initial=0)
    contract2_number_hours = forms.IntegerField(min_value=0, initial=0)
    contract3_number_hours = forms.IntegerField(min_value=0, initial=0)

    def clean_company_name(self):
        company_name = self.cleaned_data['company_name']
        if(Company.objects.filter(name=company_name).exists()):
            raise forms.ValidationError(_("This company already exists"))
        return company_name

    def save_company_and_contracts(self):
        company_name = self.cleaned_data['company_name']
        company = Company.objects.create(name=company_name)
        maintenance_types = MaintenanceType.objects.all()

        contract1_visible = self.cleaned_data['contract1_visible']
        if(contract1_visible != INACTIF_CONTRACT_INPUT):
            contract1_number_hours = self.cleaned_data['contract1_number_hours']
            contract1_total_type = self.cleaned_data['contract1_total_type']
            MaintenanceContract.objects.create(company=company,
                                               maintenance_type=maintenance_types[0],
                                               visible=bool(contract1_visible),
                                               number_hours=contract1_number_hours,
                                               total_type=contract1_total_type)

        contract2_visible = self.cleaned_data['contract2_visible']
        if(contract2_visible != INACTIF_CONTRACT_INPUT):
            contract2_number_hours = self.cleaned_data['contract2_number_hours']
            contract2_total_type = self.cleaned_data['contract2_total_type']
            MaintenanceContract.objects.create(company=company,
                                               maintenance_type=maintenance_types[1],
                                               visible=bool(contract2_visible),
                                               number_hours=contract2_number_hours,
                                               total_type=contract2_total_type)

        contract3_visible = self.cleaned_data['contract3_visible']
        if(contract3_visible != INACTIF_CONTRACT_INPUT):
            contract3_number_hours = self.cleaned_data['contract3_number_hours']
            contract3_total_type = self.cleaned_data['contract3_total_type']
            MaintenanceContract.objects.create(company=company,
                                               maintenance_type=maintenance_types[2],
                                               visible=bool(contract3_visible),
                                               number_hours=contract3_number_hours,
                                               total_type=contract3_total_type)
