from django import forms

from .models import GeneralInformation


class GeneralInformationModelForm(forms.ModelForm):
    class Meta:
        model = GeneralInformation
        fields = ("name", "email", "address", "website", "phone")
