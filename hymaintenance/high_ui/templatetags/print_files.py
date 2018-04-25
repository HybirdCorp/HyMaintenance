
import os

from django.template import Library


register = Library()


@register.filter
def file_name(value):
    return os.path.split(value.name)[-1]
