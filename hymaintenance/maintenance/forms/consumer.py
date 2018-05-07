from django import forms

from ..models import MaintenanceConsumer


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
