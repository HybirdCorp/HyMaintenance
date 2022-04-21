from invoke import task


@task
def install_req(c, lints=True, tests=True):
    c.run("pip install -r requirements.txt")
    if lints:
        c.run("pip install -r requirements_lints.txt")
    if tests:
        c.run("pip install -r requirements_tests.txt")
