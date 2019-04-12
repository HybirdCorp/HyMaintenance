from django import forms


class RecurrenceContractsModelFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super().__init__(*args, **kwargs)
        self.queryset = self.company.contracts.filter_enabled_and_available_counter()
