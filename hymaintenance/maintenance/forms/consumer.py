from django import forms

from ..models import MaintenanceConsumer


class MaintenanceConsumerModelForm(forms.ModelForm):
    class Meta:
        model = MaintenanceConsumer
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.company = self.company
        return super().save(commit)


class MaintenanceConsumersUpdateForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=None
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        self.fields['users'].queryset = MaintenanceConsumer.objects.filter(company=self.company)
        self.fields['users'].initial = MaintenanceConsumer.objects.filter(company=self.company, is_used=True)

    def save(self):
        for consumer in self.cleaned_data['users'].filter(is_used=False):
            consumer.is_used = True
            consumer.save()
        consumers_set = set(self.cleaned_data['users'])
        for consumer in self.fields['users'].queryset.filter(is_used=True):
            if consumer not in consumers_set:
                consumer.is_used = False
                consumer.save()
