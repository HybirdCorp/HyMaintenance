from invoke import call
from invoke import task


@task
def install_req(c, develop=True):
    if develop:
        c.run("pip install -r hymaintenance/requirements/develop.txt")
    else:
        c.run("pip install -r hymaintenance/requirements/requirements.txt")


@task
def install_precommit(c):
    c.run("pip install pre-commit")
    c.run("pre-commit install")


@task
def install_pip_tools(c):
    if not c.run("pip list | grep pip-tools", hide=True, warn=True).ok:
        c.run("pip install pip-tools")


@task(pre=[call(install_pip_tools)])
def update_req_txt(c):
    c.run("pip-compile --upgrade hymaintenance/requirements/develop.in")
    c.run("pip-compile --upgrade hymaintenance/requirements/requirements.in")
