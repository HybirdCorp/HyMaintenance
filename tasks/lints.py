from invoke import call
from invoke import task

from . import PNAME


@task
def black(c, check=False):
    if check:
        c.run(f"black --check -l120 {PNAME}", warn=True)
        c.run("black --check -l120 tasks", warn=True)
    else:
        c.run(f"black -l120 {PNAME}")
        c.run("black -l120 tasks")


@task
def isort(c, check=False):
    if check:
        c.run(f"isort --atomic --check-only {PNAME}", warn=True)
        c.run("isort --atomic --check-only tasks", warn=True)
    else:
        c.run(f"isort --atomic {PNAME}")
        c.run("isort --atomic tasks")


@task
def flake8(c):
    c.run(f"flake8 --show-source {PNAME}", warn=True)
    c.run("flake8 --show-source tasks", warn=True)


@task(pre=[call(black, check=True), call(isort, check=True), flake8])
def lints(c):
    pass


@task(pre=[black, isort])
def autolints(c):
    pass
