from django import forms


# return object instead of string to have the email on the template
class UsersMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj
