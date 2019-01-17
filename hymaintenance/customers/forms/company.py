import os
import re

from PIL import Image

from django import forms
from django.utils.translation import ugettext_lazy as _

from toolkit.forms import HyClearableFileInput

from ..models import Company


class ProjectCustomizeForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "contact", "logo", "color", "dark_font_color")
        widgets = {"logo": HyClearableFileInput, "dark_font_color": forms.HiddenInput()}

    def clean_color(self):
        color = self.cleaned_data["color"]
        if color and not re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
            self.add_error("color", _("Invalid hexadecimal color code: '%s'") % color)
        return color

    def save(self):
        old_company = Company.objects.get(id=self.instance.id)

        project = super().save()
        if old_company.logo and old_company.logo != project.logo:
            os.remove(old_company.logo.path)

        if project.logo:
            image = Image.open(project.logo)
            image.thumbnail((125, 75))
            image.save(project.logo.path)

        return project
