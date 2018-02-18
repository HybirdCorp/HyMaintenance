from random import randint

from django.template import Library


register = Library()


@register.simple_tag
def random_background():
    return randint(1, 7)
