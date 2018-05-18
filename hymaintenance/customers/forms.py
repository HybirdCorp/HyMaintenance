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
        user = super().save(commit=False)
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


class ManagerUsersUpdateForm(forms.Form):
    managers = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=None
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        self.fields['managers'].queryset = MaintenanceUser.objects.filter(
            company=self.company, is_staff=False)
        self.fields['managers'].initial = MaintenanceUser.objects.filter(
            company=self.company, is_staff=False, is_active=True)

    def save(self):
        for manager in self.cleaned_data['managers'].filter(is_active=False):
            manager.is_active = True
            manager.save()
        managers_set = set(self.cleaned_data['managers'])
        for manager in self.fields['managers'].queryset.filter(is_active=True):
            if manager not in managers_set:
                manager.is_active = False
                manager.save()


class OperatorUserCreateForm(MaintenanceUserCreateForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        super().__init__(*args, **kwargs)

    def fill_user(self, user):
        user.is_staff = True

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.operator_for.add(self.company)
        return user


class OperatorUserArchiveForm(forms.Form):
    active_operators = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=True)
    )

    def save(self):
        for operator in self.cleaned_data['active_operators']:
            operator.is_active = False
            operator.save()


class OperatorUserUnarchiveForm(forms.Form):
    inactive_operators = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=False)
    )

    def save(self):
        for operator in self.cleaned_data['inactive_operators']:
            operator.is_active = True
            operator.save()
