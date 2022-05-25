from invoke import task

from . import PNAME


@task
def makemessages(c):
    c.run(f"cd {PNAME} && django-admin makemessages -l fr && cd -")


@task
def compilemessages(c):
    c.run(f"cd {PNAME} && django-admin compilemessages && cd -")
