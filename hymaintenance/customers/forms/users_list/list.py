from django import forms
from django.db.models import Count
from django.utils.html import format_html
from django.utils.translation import gettext as _

from ...models import MaintenanceUser



def print_operator_projects(operator):
    project_names = [project.name for project in operator.operator_for.all()]
    project_number = len(project_names)
    if project_number < 1:
        return format_html(_("project: none"))
    elif project_number == 1:
        return format_html(_("project: {}"), project_names[0])
    else:
        return format_html(_("projects: {}"), ", ".join(project_names))



class OperatorModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        description = print_operator_projects(obj)
        return obj.get_full_name(), description


class OperatorUsersListArchiveForm(forms.Form):
    active_users = OperatorModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=True).prefetch_related("operator_for"),
    )

    def save(self):
        for user in self.cleaned_data["active_users"]:
            user.is_active = False
            user.save()


class OperatorUsersListUnarchiveForm(forms.Form):
    inactive_users = OperatorModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_operator_users_queryset().filter(is_active=False).prefetch_related("operator_for"),
    )

    def save(self):
        for user in self.cleaned_data["inactive_users"]:
            user.is_active = True
            user.save()


class AdminUsersListArchiveForm(forms.Form):
    active_users = OperatorModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_admin_users_queryset().filter(is_active=True).prefetch_related("operator_for"),
    )

    def save(self):
        for user in self.cleaned_data["active_users"]:
            user.is_active = False
            user.save()


class AdminUsersListUnarchiveForm(forms.Form):
    inactive_users = OperatorModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=MaintenanceUser.objects.get_admin_users_queryset().filter(is_active=False).prefetch_related("operator_for"),
    )

    def save(self):
        for user in self.cleaned_data["inactive_users"]:
            user.is_active = True
            user.save()
