import datetime

from customers.models import Company
from customers.models import MaintenanceUser

from django import forms
from django.utils.translation import ugettext_lazy as _

from ..models import MaintenanceContract
from ..models import MaintenanceCredit
from ..models import MaintenanceType
from ..models.contract import AVAILABLE_TOTAL_TIME


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
    displayed_month_number = forms.IntegerField(label=_("Historic"), required=True, widget=forms.TextInput(), initial=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maintenance_types = MaintenanceType.objects.order_by("id")
        for index, maintenance_type in enumerate(self.maintenance_types):
            self.fields[f"contract{index}_counter_name"] = forms.CharField(
                label=_("Counter name"),
                max_length=255,
                required=True
            )

            self.fields[f"contract{index}_date"] = forms.DateField(
                label=_("Start Date"),
                initial=datetime.date.today,
                required=True
            )

            self.fields[f"contract{index}_visible"] = forms.IntegerField(
                label=_("Counter"),
                widget=forms.HiddenInput()
            )

            self.fields[f"contract{index}_total_type"] = forms.IntegerField(
                label=_("Counter type"),
                widget=forms.HiddenInput()
            )


class ProjectCreateForm(ProjectForm):
    error_messages = {"no_contract": _("You have to create at least one contract on the project.")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for index, maintenance_type in enumerate(self.maintenance_types):
            self.fields[f"contract{index}_credited_hours"] = forms.IntegerField(
                label=_("Credited hours"),
                min_value=0,
                initial=0,
                widget=forms.TextInput()
            )

            self.initial[f"contract{index}_counter_name"] = maintenance_type.name

    def clean_company_name(self):
        company_name = self.cleaned_data["company_name"]
        if Company.objects.filter(name=company_name).exists():
            raise forms.ValidationError(_("This company already exists."))
        return company_name

    def clean(self):
        cleaned_data = super().clean()
        if not self.errors:
            all_disabled = True
            for index, maintenance_type in enumerate(self.maintenance_types):
                all_disabled = all_disabled and (True if cleaned_data[f"contract{index}_visible"] == -1 else False)
            if all_disabled:
                raise forms.ValidationError(self.error_messages["no_contract"], code="no_contract")
        return cleaned_data

    def create_contract(self, index, maintenance_type, company):
        contract_counter_name = self.cleaned_data[f"contract{index}_counter_name"]
        if contract_counter_name == maintenance_type.name:
            contract_counter_name = ""

        form_contract_visible = self.cleaned_data[f"contract{index}_visible"]
        contract_total_type = self.cleaned_data[f"contract{index}_total_type"]
        contract_date = self.cleaned_data[f"contract{index}_date"]

        contract_data = {
            "counter_name": contract_counter_name,
            "start": contract_date,
            "company": company,
            "maintenance_type": maintenance_type,
            "visible": bool(form_contract_visible) if form_contract_visible != -1 else False,
            "disabled": True if form_contract_visible == -1 else False,
            "total_type": contract_total_type
        }
        contract = MaintenanceContract.objects.create(**contract_data)

        contract_credited_hours = self.cleaned_data[f"contract{index}_credited_hours"]
        if contract_total_type == AVAILABLE_TOTAL_TIME:
            MaintenanceCredit.objects.create(
                company=company, contract=contract, date=contract_date, hours_number=contract_credited_hours
            )

    def create_company_and_contracts(self):
        company_data = {
            "name": self.cleaned_data["company_name"],
            "displayed_month_number": self.cleaned_data["displayed_month_number"],
        }

        if self.cleaned_data["contact"]:
            company_data["contact"] = self.cleaned_data["contact"]

        company = Company.objects.create(**company_data)

        for operator in MaintenanceUser.objects.get_active_operator_users_queryset():
            operator.operator_for.add(company)

        for index, maintenance_type in enumerate(self.maintenance_types):
            self.create_contract(index, maintenance_type, company)


class ProjectUpdateForm(ProjectForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        self.contracts = list(self.company.contracts.order_by("maintenance_type_id"))
        super().__init__(*args, **kwargs)
        self.fields["company_name"].initial = self.company.name
        self.fields["contact"].initial = self.company.contact
        self.fields["contact"].queryset = self.company.managed_by.all()
        self.fields["displayed_month_number"].initial = self.company.displayed_month_number

        recipients = MaintenanceUser.objects.filter(
            is_staff=False, is_superuser=False, company=self.company, is_active=True
        )

        for index, maintenance_type in enumerate(self.maintenance_types):
            self.fields[f"contract{index}_email_alert"] = forms.BooleanField(
                label=_("Email Alert"),
                required=False,
                widget=forms.HiddenInput()
            )
            self.fields[f"contract{index}_credited_hours_min"] = forms.IntegerField(
                label=_("Hour threshold"),
                required=False,
                min_value=0,
                initial=0,
                widget=forms.TextInput()
            )
            self.fields[f"contract{index}_recipient"] = forms.ModelChoiceField(
                label=_("To contact"),
                empty_label=None,
                required=False,
                queryset=None
            )

            self.fields[f"contract{index}_counter_name"].initial = self.contracts[index].get_counter_name()
            self.fields[f"contract{index}_date"].initial = self.contracts[index].start
            visibile_initial = -1 if self.contracts[index].disabled else int(self.contracts[index].visible)
            self.fields[f"contract{index}_visible"].initial = visibile_initial
            self.fields[f"contract{index}_total_type"].initial = self.contracts[index].total_type

            self.fields[f"contract{index}_recipient"].queryset = recipients
            self.fields[f"contract{index}_email_alert"].initial = self.contracts[index].email_alert
            self.fields[f"contract{index}_credited_hours_min"].initial = self.contracts[index].credited_hours_min
            self.fields[f"contract{index}_recipient"].initial = self.contracts[index].recipient

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
                contract.compute_and_set_credited_hours()

        contract_email_alert = self.cleaned_data[f"contract{index}_email_alert"]
        if contract.email_alert != contract_email_alert:
            contract_is_modified = True
            contract.email_alert = contract_email_alert

        contract_credited_hours_min = self.cleaned_data[f"contract{index}_credited_hours_min"]
        if contract.credited_hours_min != contract_credited_hours_min:
            contract_is_modified = True
            contract.credited_hours_min = contract_credited_hours_min

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

        company_displayed_month_number = self.cleaned_data["displayed_month_number"]
        if self.company.displayed_month_number != company_displayed_month_number:
            self.company.displayed_month_number = company_displayed_month_number
            company_is_modified = True

        if company_is_modified:
            self.company.save()

        for index, maintenance_type in enumerate(self.maintenance_types):
            self.update_contract(index, self.contracts[index])
