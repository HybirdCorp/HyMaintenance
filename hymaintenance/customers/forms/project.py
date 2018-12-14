from django import forms

from ..models import Company


class ProjectListUnarchiveForm(forms.Form):
    projects = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=Company.objects.filter(is_archived=True).order_by("name"),
    )

    def save(self):
        for project in self.cleaned_data["projects"]:
            project.is_archived = False
            project.save()


class ProjectListArchiveForm(forms.Form):
    projects = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=Company.objects.filter(is_archived=False).order_by("name"),
    )

    def save(self):
        for project in self.cleaned_data["projects"]:
            project.is_archived = True
            project.save()
