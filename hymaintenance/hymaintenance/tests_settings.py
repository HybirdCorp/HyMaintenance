
from .settings import *  # noqa: F403


MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

ALLOWED_HOSTS = "*"
DEBUG = True

RAVEN = "raven.contrib.django.raven_compat"
if RAVEN in INSTALLED_APPS:  # noqa: F405
    INSTALLED_APPS.remove(RAVEN)  # noqa: F405

TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa: F405


class InvalidStringShowWarning(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError

        raise TemplateSyntaxError("Invalid variable : '%s'" % other)


TEMPLATES[0]["OPTIONS"]["string_if_invalid"] = ""  # InvalidStringShowWarning("%s")  # noqa: F405
