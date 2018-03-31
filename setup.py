#!/usr/bin/env python
from distutils.core import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
      long_description = f.read()


classifiers=[
    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5'
]
setup(name='django-lifecycle',
      version='0.1.2',
      description='Declarative model lifecycle hooks, inspired by Rails callbacks.',
      author='Robert Singer',
      author_email='robertgsinger@gmail.com',
      packages=['django_lifecycle'],
      url='https://github.com/rsinger86/django-lifecycle',
      license='MIT',
      keywords='django model lifecycle hooks callbacks',
      long_description=long_description,
      classifiers=classifiers
)