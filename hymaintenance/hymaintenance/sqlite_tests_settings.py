import os

from .tests_settings import *  # noqa: F403


DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "db2.sqlite3")}  # noqa: F405
}
