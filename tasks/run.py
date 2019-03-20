from string import Template

from invoke import task

from . import PNAME
from .lints import lints


COV_OMIT_VALUE = f"{PNAME}/manage.py,**/migrations/*,**/admin.py,{PNAME}/{PNAME}/*"
COV_LAUNCH = Template(
    f"coverage run --branch --source={PNAME} {PNAME}/manage.py test {PNAME} " f"--settings {PNAME}.$tests_settings"
)
COV_REPORT = f"coverage report -m --omit={COV_OMIT_VALUE} --skip-covered"
COV_XML = f"coverage xml --omit={COV_OMIT_VALUE}"

TESTS_LAUNCH = Template(
    f"python {PNAME}/manage.py test {PNAME} --parallel=4 " f"--settings={PNAME}.$tests_settings --noinput"
)

MIGRATE = Template(f"python {PNAME}/manage.py migrate --settings={PNAME}.$settings")

SERVE = Template(f"python {PNAME}/manage.py runserver --settings={PNAME}.$settings")


@task(aliases=["tests"])
def run_tests_and_coverage(c):
    c.run(COV_LAUNCH.substitute(tests_settings="tests_settings"))
    c.run(COV_REPORT)
    c.run(COV_XML)


@task
def run_sqlite_tests_and_coverage(c):
    c.run(COV_LAUNCH.substitute(tests_settings="sqlite_tests_settings"))
    c.run(COV_REPORT)


@task
def run_sqlite_only_tests(c):
    c.run(TESTS_LAUNCH.substitute(tests_settings="sqlite_tests_settings"))


@task
def run_only_tests(c):
    c.run(TESTS_LAUNCH.substitute(tests_settings="tests_settings"))


@task(pre=[lints, run_tests_and_coverage])
def all_included(c):
    pass


@task
def migrate(c):
    c.run(MIGRATE.substitute(settings="sqlite_tests_settings"))


@task
def serve(c):
    c.run(SERVE.substitute(settings="sqlite_tests_settings"))
