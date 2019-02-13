import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from customers.models import Company
from customers.models import MaintenanceUser

from ..models import MaintenanceContract
from ..models import MaintenanceCredit
from ..models import MaintenanceType
from ..models.contract import AVAILABLE_TOTAL_TIME
from ..models.credit import calcul_number_hours


INACTIF_CONTRACT_INPUT = -1


# TODO: limit the "user_who_fix" choices to valid MaintenanceUsers
# TODO: similarly, limit the consumer_who_ask MaintenanceConsumer to the current company ones
class ProjectForm(forms.Form):
    company_name = forms.CharField(label=_("Company"), max_length=255, required=True)
    contact = forms.ModelChoiceField(
        label=_("Contact"),
        required=False,
        widget=forms.Select,
        queryset=MaintenanceUser.objects.get_active_operator_users_queryset(),
    )
    contract1_counter_name = forms.CharField(label=_("Counter name"), max_length=255, required=True)
    contract2_counter_name = forms.CharField(label=_("Counter name"), max_length=255, required=True)
    contract3_counter_name = forms.CharField(label=_("Counter name"), max_length=255, required=True)
    contract1_date = forms.DateField(label=_("Start Date"), initial=datetime.date.today, required=True)
    contract2_date = forms.DateField(label=_("Start Date"), initial=datetime.date.today, required=True)
    contract3_date = forms.DateField(label=_("Start Date"), initial=datetime.date.today, required=True)
    contract1_visible = forms.IntegerField(label=_("Counter"), widget=forms.HiddenInput())
    contract2_visible = forms.IntegerField(label=_("Counter"), widget=forms.HiddenInput())
    contract3_visible = forms.IntegerField(label=_("Counter"), widget=forms.HiddenInput())
    contract1_total_type = forms.IntegerField(label=_("Counter type"), widget=forms.HiddenInput())
    contract2_total_type = forms.IntegerField(label=_("Counter type"), widget=forms.HiddenInput())
    contract3_total_type = forms.IntegerField(label=_("Counter type"), widget=forms.HiddenInput())


class ProjectCreateForm(ProjectForm):
    error_messages = {"no_contract": _("You have to create at least one contract on the project.")}
    contract1_number_hours = forms.IntegerField(
        label=_("Credited hours"), min_value=0, initial=0, widget=forms.TextInput()
    )
    contract2_number_hours = forms.IntegerField(
        label=_("Credited hours"), min_value=0, initial=0, widget=forms.TextInput()
    )
    contract3_number_hours = forms.IntegerField(
        label=_("Credited hours"), min_value=0, initial=0, widget=forms.TextInput()
    )

    def __init__(self, *args, **kwargs):
        maintenance_types = MaintenanceType.objects.order_by("id")
        if not kwargs.get("initial"):
            kwargs["initial"] = {}
        kwargs["initial"].update(
            {
                "contract1_counter_name": maintenance_types[0].name,
                "contract2_counter_name": maintenance_types[1].name,
                "contract3_counter_name": maintenance_types[2].name,
            }
        )
        super().__init__(*args, **kwargs)

    def clean_company_name(self):
        company_name = self.cleaned_data["company_name"]
        if Company.objects.filter(name=company_name).exists():
            raise forms.ValidationError(_("This company already exists."))
        return company_name

    def clean(self):
        cleaned_data = super().clean()
        if not self.errors:
            form_contract1_visible = cleaned_data["contract1_visible"]
            contract1_disabled = True if form_contract1_visible == -1 else False
            form_contract2_visible = cleaned_data["contract2_visible"]
            contract2_disabled = True if form_contract2_visible == -1 else False
            form_contract3_visible = cleaned_data["contract3_visible"]
            contract3_disabled = True if form_contract3_visible == -1 else False
            if contract1_disabled and contract2_disabled and contract3_disabled:
                raise forms.ValidationError(self.error_messages["no_contract"], code="no_contract")
        return cleaned_data

    def create_contract(self, index, maintenance_type, company):
        form_contract_visible = self.cleaned_data[f"contract{index}_visible"]
        contract_disabled = True if form_contract_visible == -1 else False
        contract_visible = bool(form_contract_visible) if form_contract_visible != -1 else False

        contract_number_hours = self.cleaned_data[f"contract{index}_number_hours"]
        contract_total_type = self.cleaned_data[f"contract{index}_total_type"]
        contract_date = self.cleaned_data[f"contract{index}_date"]
        contract_counter_name = self.cleaned_data[f"contract{index}_counter_name"]

        if contract_counter_name == maintenance_type.name:
            contract_counter_name = ""

        contract = MaintenanceContract.objects.create(
            counter_name=contract_counter_name,
            start=contract_date,
            company=company,
            maintenance_type=maintenance_type,
            visible=contract_visible,
            disabled=contract_disabled,
            total_type=contract_total_type,
        )

        if contract_total_type == AVAILABLE_TOTAL_TIME:
            MaintenanceCredit.objects.create(
                company=company, contract=contract, date=contract_date, hours_number=contract_number_hours
            )

    def create_company_and_contracts(self, operator=None):
        company_name = self.cleaned_data["company_name"]
        company = Company.objects.create(name=company_name)

        if self.cleaned_data["contact"] is not None:
            company.contact = self.cleaned_data["contact"]
            company.save()

        if operator:
            operator.operator_for.add(company)
        else:
            for operator in MaintenanceUser.objects.get_active_operator_users_queryset():
                operator.operator_for.add(company)

        for index, maintenance_type in enumerate(MaintenanceType.objects.order_by("id")):
            self.create_contract(index + 1, maintenance_type, company)


class ProjectUpdateForm(ProjectForm):
    contract1_email_alert = forms.BooleanField(label=_("Email Alert"), required=False, widget=forms.HiddenInput())
    contract2_email_alert = forms.BooleanField(label=_("Email Alert"), required=False, widget=forms.HiddenInput())
    contract3_email_alert = forms.BooleanField(label=_("Email Alert"), required=False, widget=forms.HiddenInput())
    contract1_number_hours_min = forms.IntegerField(
        label=_("Hour threshold"), required=False, min_value=0, initial=0, widget=forms.TextInput()
    )
    contract2_number_hours_min = forms.IntegerField(
        label=_("Hour threshold"), required=False, min_value=0, initial=0, widget=forms.TextInput()
    )
    contract3_number_hours_min = forms.IntegerField(
        label=_("Hour threshold"), required=False, min_value=0, initial=0, widget=forms.TextInput()
    )
    contract1_recipient = forms.ModelChoiceField(label=_("To contact"), empty_label=None, required=False, queryset=None)
    contract2_recipient = forms.ModelChoiceField(label=_("To contact"), empty_label=None, required=False, queryset=None)
    contract3_recipient = forms.ModelChoiceField(label=_("To contact"), empty_label=None, required=False, queryset=None)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        self.contracts = list(self.company.contracts.order_by("maintenance_type_id"))
        super().__init__(*args, **kwargs)
        self.fields["company_name"].initial = self.company.name
        self.fields["contact"].initial = self.company.contact
        self.fields["contract1_counter_name"].initial = self.contracts[0].get_counter_name()
        self.fields["contract2_counter_name"].initial = self.contracts[1].get_counter_name()
        self.fields["contract3_counter_name"].initial = self.contracts[2].get_counter_name()
        self.fields["contract1_date"].initial = self.contracts[0].start
        self.fields["contract2_date"].initial = self.contracts[1].start
        self.fields["contract3_date"].initial = self.contracts[2].start
        self.fields["contract1_visible"].initial = -1 if self.contracts[0].disabled else int(self.contracts[0].visible)
        self.fields["contract2_visible"].initial = -1 if self.contracts[1].disabled else int(self.contracts[1].visible)
        self.fields["contract3_visible"].initial = -1 if self.contracts[2].disabled else int(self.contracts[2].visible)
        self.fields["contract1_total_type"].initial = self.contracts[0].total_type
        self.fields["contract2_total_type"].initial = self.contracts[1].total_type
        self.fields["contract3_total_type"].initial = self.contracts[2].total_type

        recipients = MaintenanceUser.objects.filter(
            is_staff=False, is_superuser=False, company=self.company, is_active=True
        )
        self.fields["contract1_recipient"].queryset = recipients
        self.fields["contract2_recipient"].queryset = recipients
        self.fields["contract3_recipient"].queryset = recipients
        self.fields["contract1_email_alert"].initial = self.contracts[0].email_alert
        self.fields["contract2_email_alert"].initial = self.contracts[1].email_alert
        self.fields["contract3_email_alert"].initial = self.contracts[2].email_alert
        self.fields["contract1_number_hours_min"].initial = self.contracts[0].number_hours_min
        self.fields["contract2_number_hours_min"].initial = self.contracts[1].number_hours_min
        self.fields["contract3_number_hours_min"].initial = self.contracts[2].number_hours_min
        self.fields["contract1_recipient"].initial = self.contracts[0].recipient
        self.fields["contract2_recipient"].initial = self.contracts[1].recipient
        self.fields["contract3_recipient"].initial = self.contracts[2].recipient

    def clean_company_name(self):
        company_name = self.cleaned_data["company_name"]
        if Company.objects.filter(name=company_name).exclude(id=self.company.id).exists():
            raise forms.ValidationError(_("This company already exists."))
        return company_name

    def update_contract(self, index, contract):
        contract_is_modified = False
        contract_counter_name = self.cleaned_data[f"contract{index}_counter_name"]
        if contract_counter_name == contract.maintenance_type.name:
            contract_counter_name = ""
        if contract.counter_name != contract_counter_name:
            contract_is_modified = True
            contract.counter_name = contract_counter_name

        contract_date = self.cleaned_data[f"contract{index}_date"]
        if contract.start != contract_date:
            contract_is_modified = True
            contract.start = contract_date

        contract_disabled = self.cleaned_data[f"contract{index}_visible"] == -1
        if contract.disabled != contract_disabled:
            contract_is_modified = True
            contract.disabled = contract_disabled

        contract_visible = self.cleaned_data[f"contract{index}_visible"] == 1
        if contract.visible != contract_visible:
            contract_is_modified = True
            contract.visible = contract_visible

        contract_total_type = self.cleaned_data[f"contract{index}_total_type"]
        if contract.total_type != contract_total_type:
            contract_is_modified = True
            contract.total_type = contract_total_type
            if contract.total_type == AVAILABLE_TOTAL_TIME:
                contract.number_hours = calcul_number_hours(contract)

        contract_email_alert = self.cleaned_data[f"contract{index}_email_alert"]
        if contract.email_alert != contract_email_alert:
            contract_is_modified = True
            contract.email_alert = contract_email_alert

        contract_number_hours_min = self.cleaned_data[f"contract{index}_number_hours_min"]
        if contract.number_hours_min != contract_number_hours_min:
            contract_is_modified = True
            contract.number_hours_min = contract_number_hours_min

        contract_recipient = self.cleaned_data[f"contract{index}_recipient"]
        if contract.recipient != contract_recipient:
            contract_is_modified = True
            contract.recipient = contract_recipient

        if contract_is_modified:
            contract.save()

    def update_company_and_contracts(self):
        company_is_modified = False
        company_name = self.cleaned_data["company_name"]
        if self.company.name != company_name:
            self.company.name = company_name
            company_is_modified = True

        company_contact = self.cleaned_data["contact"]
        if self.company.contact != company_contact:
            self.company.contact = company_contact
            company_is_modified = True

        if company_is_modified:
            self.company.save()

        self.update_contract(1, self.contracts[0])
        self.update_contract(2, self.contracts[1])
        self.update_contract(3, self.contracts[2])
