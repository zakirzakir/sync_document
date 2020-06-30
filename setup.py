# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in sync_document/__init__.py
from sync_document import __version__ as version

setup(
	name='sync_document',
	version=version,
	description=' ',
	author='DAS',
	author_email=' ',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
