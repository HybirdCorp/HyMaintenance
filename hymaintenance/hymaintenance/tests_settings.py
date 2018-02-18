
from .settings import *  # noqa: F405, F401


ALLOWED_HOSTS = '*'
DEBUG = True
INSTALLED_APPS.extend(['django_extensions', 'debug_toolbar'])

RAVEN = 'raven.contrib.django.raven_compat'
if RAVEN in INSTALLED_APPS:
    INSTALLED_APPS.remove(RAVEN)

TEMPLATES[0]['OPTIONS']['debug'] = True


class InvalidStringShowWarning(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError
        raise TemplateSyntaxError("Invalid variable : '%s'" % other)


TEMPLATES[0]['OPTIONS']['string_if_invalid'] = ""  # InvalidStringShowWarning("%s")
