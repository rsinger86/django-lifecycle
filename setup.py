#!/usr/bin/env python
from distutils.core import setup
from codecs import open
from os import path


def readme():
    with open("README.txt", "r") as infile:
        return infile.read()


classifiers = [
    # Pick your license as you wish (should match "license" above)
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]
setup(
    name="django-lifecycle",
    version="0.4.0",
    description="Declarative model lifecycle hooks, inspired by Rails callbacks.",
    author="Robert Singer",
    author_email="robertgsinger@gmail.com",
    packages=["django_lifecycle"],
    url="https://github.com/rsinger86/django-lifecycle",
    license="MIT",
    keywords="django model lifecycle hooks callbacks",
    long_description=readme(),
    classifiers=classifiers,
)
