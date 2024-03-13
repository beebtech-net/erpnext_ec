# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ast
import re

from setuptools import find_packages, setup

# get version from __version__ variable in erpnext/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('requirements.txt') as f:
        install_requires = f.read().strip().split('\n')

with open('erpnext_ec/__init__.py', 'rb') as f:
        version = str(ast.literal_eval(_version_re.search(
                f.read().decode('utf-8')).group(1)))

setup(
        name='erpnext_ec',
        version=version,
        description='ErpNext Ecuador',
        author='BeebTech Studios',
        author_email='ronald.chonillo@beebtech.net',
        packages=find_packages(),
        zip_safe=False,
        include_package_data=True,
        install_requires=install_requires
)
