from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from .models import Company
from .models import MaintenanceUser


class CompanyAdmin(admin.ModelAdmin):
    model = Company
    fields = ("name", "maintenance_contact")
    list_display = ("name", "maintenance_contact")


class MaintenanceUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    error_messages = {"password_mismatch": _("The two password fields didn't match.")}
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."),
    )

    class Meta:
        model = MaintenanceUser
        fields = ("email", "company")

    def __init__(self, *args, **kwargs):
        super(MaintenanceUserCreationForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages["password_mismatch"], code="password_mismatch")
        return password2

    def save(self, commit=True):
        user = super(MaintenanceUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class MaintenanceUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="password/">this form</a>.'
        ),
    )

    class Meta:
        model = MaintenanceUser
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(MaintenanceUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get("user_permissions", None)
        if f is not None:
            f.queryset = f.queryset.select_related("content_type")

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class MaintenanceUserAdmin(BaseUserAdmin):
    model = MaintenanceUser
    form = MaintenanceUserChangeForm
    add_form = MaintenanceUserCreationForm

    fieldsets = (
        (None, {"fields": ("email", "password", "company")}),
        (
            _("Permissions"),
            {
                "classes": ("collapse",),
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
            },
        ),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "company", "password1", "password2")}),)
    list_display = ("email", "company", "first_name", "last_name")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("user_permissions",)


admin.site.register(Company, CompanyAdmin)
admin.site.register(MaintenanceUser, MaintenanceUserAdmin)
