from django import forms
from django.forms.widgets import ClearableFileInput


# return object instead of string to have the email on the template
class UsersMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj


class HyClearableFileInput(ClearableFileInput):
    template_name = "toolkit/forms/widgets/attachment.html"
