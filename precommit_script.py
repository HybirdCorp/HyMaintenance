#!/usr/bin/env python

import sys

from flake8.main import git
from isort.hooks import git_hook

if __name__ == '__main__':

    flake8_return = git.hook(strict=True, lazy=True)
    isort_return = git_hook(strict=True)
    sys.exit(flake8_return + isort_return)
