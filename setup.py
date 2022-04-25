# -*- coding: utf-8 -*-

import os
import re
from typing import Iterator

import setuptools


REQUIREMENTS_FOLDER = os.path.join(
    os.path.dirname(__file__), "hymaintenance", "requirements")


def read_dependencies(filename: str) -> Iterator[str]:
    """
    Read a requirements file present in the `requirements` folder.
    Those files are outputs of `pip-compile` from `pip-tools`.
    Exclude comments, and pip flags.
    """
    filepath = os.path.join(REQUIREMENTS_FOLDER, filename)
    with open(filepath) as _file:
        req_content = _file.read().replace("\\\n", "").split("\n")

    for line in req_content:
        line = re.sub(r" *(#|--).*$", "", line.strip()).strip()
        if line:
            yield line


setuptools.setup(
    install_requires=list(read_dependencies("requirements.txt")),
    extras_require={
        'develop': list(read_dependencies("develop.txt")),
    }
)
