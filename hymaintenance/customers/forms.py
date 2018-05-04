from django import forms

from .models import Company, MaintenanceUser


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name', 'maintenance_contact')


class MaintenanceUserCreateForm(forms.ModelForm):
    class Meta:
        model = MaintenanceUser
        fields = ('first_name', 'last_name', 'email', 'password')
        widgets = {'password': forms.PasswordInput()}

    def save(self, commit=True):
        user = super(MaintenanceUserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])

        self.fill_user(user)

        if commit:
            user.save()
        return user

    def fill_user(self, user):
        """Extending classes can modify the user here before it is saved.
        This default implementation does nothing, no need to call super
        """
        pass


class ManagerUserCreateForm(MaintenanceUserCreateForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)

    def fill_user(self, user):
        user.company = self.company


class OperatorUserCreateForm(MaintenanceUserCreateForm):
    def fill_user(self, user):
        user.is_staff = True
