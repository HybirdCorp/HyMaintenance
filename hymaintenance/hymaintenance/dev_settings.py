
from .settings import *  # noqa: F403


DEBUG_TOOLBAR = "debug_toolbar"
RAVEN = "raven.contrib.django.raven_compat"

ALLOWED_HOSTS = ["*"]
DEBUG = True

if DEBUG_TOOLBAR not in INSTALLED_APPS:  # noqa: F405
    INSTALLED_APPS.append(DEBUG_TOOLBAR)  # noqa: F405

if RAVEN in INSTALLED_APPS:  # noqa: F405
    INSTALLED_APPS.remove(RAVEN)  # noqa: F405

MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
