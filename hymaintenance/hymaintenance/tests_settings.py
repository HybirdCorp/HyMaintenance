
from .settings import *  # noqa: F403


ALLOWED_HOSTS = ["*"]
DEBUG = True

TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa: F405


class InvalidStringShowWarning(str):
    def __mod__(self, other):
        from django.template.base import TemplateSyntaxError

        raise TemplateSyntaxError("Invalid variable : '%s'" % other)


TEMPLATES[0]["OPTIONS"]["string_if_invalid"] = ""  # InvalidStringShowWarning("%s")  # noqa: F405
