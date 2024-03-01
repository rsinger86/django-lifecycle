#!/usr/bin/env python
import codecs
import os
import re
from codecs import open

from setuptools import setup


def get_metadata(package, field):
    """
    Return package data as listed in `__{field}__` in `init.py`.
    """
    with codecs.open(os.path.join(package, "__init__.py"), encoding="utf-8") as fp:
        init_py = fp.read()
    return re.search("^__{}__ = ['\"]([^'\"]+)['\"]".format(field), init_py, re.MULTILINE).group(1)


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    # Pick your license as you wish (should match "license" above)
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Framework :: Django",
    "Framework :: Django :: 2.2",
    "Framework :: Django :: 3.2",
    "Framework :: Django :: 4.0",
    "Framework :: Django :: 4.1",
    "Framework :: Django :: 4.2",
    "Framework :: Django :: 5.0",
]
setup(
    name="django-lifecycle",
    version=get_metadata("django_lifecycle", "version"),
    description="Declarative model lifecycle hooks.",
    author=get_metadata("django_lifecycle", "author"),
    author_email=get_metadata("django_lifecycle", "author_email"),
    packages=["django_lifecycle", "django_lifecycle_checks", "django_lifecycle.conditions"],
    url="https://github.com/rsinger86/django-lifecycle",
    project_urls={
        "Documentation": "https://rsinger86.github.io/django-lifecycle/",
        "Source": "https://github.com/rsinger86/django-lifecycle",
    },
    license="MIT",
    keywords="django model lifecycle hooks callbacks",
    long_description=readme(),
    classifiers=classifiers,
    long_description_content_type="text/markdown",
    install_requires=["Django>=3.2"],
    tests_require=[
        "urlman>=1.2.0",
        "django-capture-on-commit-callbacks",
    ],
)
