# -*- coding: utf-8 -*-

import os
import setuptools


EXCLUDE_FROM_PACKAGES = []

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name='HyMaintenance',
    version='0.1.0',
    author="Hybird",
    description="HyMaintenance",
    author_email='',
    url='',
    license='',
    packages=setuptools.find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    zip_safe=False,
)
