
import os

from django.template import Library


register = Library()


@register.filter
def file_name(value):
    return os.path.basename(value.file.name)
