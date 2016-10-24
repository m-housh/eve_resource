#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'Eve>=0.6.4'
]

test_requirements = [
    'pytest>=2.9.2',
    'pytest-cov>=2.2.1',
    # TODO: put package test requirements here
]

setup_requirements = [
    'pytest-runner',
]

setup(
    name='eve_resource',
    version='0.1.2',
    description="Resource utilities for Eve",
    long_description=readme + '\n\n' + history,
    author="Michael Housh",
    author_email='mhoush@houshhomeenergy.com',
    url='https://github.com/m-housh/eve_resource',
    packages=find_packages(),
    package_dir={'eve_resource':
                 'eve_resource'},
    include_package_data=True,
    install_requires=requirements,
    setup_requires=setup_requirements,
    license="MIT license",
    zip_safe=False,
    keywords='eve_resource',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='eve_resource/test',
    tests_require=test_requirements
)
