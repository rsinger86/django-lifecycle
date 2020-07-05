#!/usr/bin/env python
import codecs
import os
import re

from setuptools import setup
from codecs import open


def get_metadata(package, field):
    """
    Return package data as listed in `__{field}__` in `init.py`.
    """
    init_py = codecs.open(os.path.join(package, "__init__.py"), encoding="utf-8").read()
    return re.search(
        "^__{}__ = ['\"]([^'\"]+)['\"]".format(field), init_py, re.MULTILINE
    ).group(1)


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    # Pick your license as you wish (should match "license" above)
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Framework :: Django",
    "Framework :: Django :: 2.0",
    "Framework :: Django :: 2.1",
    "Framework :: Django :: 2.2",
    "Framework :: Django :: 3.0",
]
setup(
    name="django-lifecycle",
    version=get_metadata("django_lifecycle", "version"),
    description="Declarative model lifecycle hooks.",
    author=get_metadata("django_lifecycle", "author"),
    author_email=get_metadata("django_lifecycle", "author_email"),
    packages=["django_lifecycle"],
    url="https://github.com/rsinger86/django-lifecycle",
    license="MIT",
    keywords="django model lifecycle hooks callbacks",
    long_description=readme(),
    classifiers=classifiers,
    long_description_content_type="text/markdown",
    install_requires=[
        "Django>=2.0",
        "urlman>=1.2.0"
    ],
)
