from invoke import task


@task
def install_req(c, lints=True):
    c.run("pip install -r requirements.txt")
    if lints:
        c.run("pip install -r requirements_lints.txt")
