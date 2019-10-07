# Django Lifecycle Hooks

[![Package version](https://badge.fury.io/py/django-lifecycle.svg)](https://pypi.python.org/pypi/django-lifecycle)
[![Python versions](https://img.shields.io/pypi/status/django-lifecycle.svg)](https://img.shields.io/pypi/status/django-lifecycle.svg/)

# Overview

This project provides a `@hook` decorator as well as a base model or mixin to add lifecycle hooks to your Django models. Django's built-in approach to offering lifecycle hooks is [Signals](https://docs.djangoproject.com/en/2.0/topics/signals/). However, in the projects I've worked on, my team often finds that Signals introduce unnesseary indirection and are at odds with Django's "fat models" approach of including related logic in the model class itself*. 

In short, you can write model code that looks like this:

```python
from django_lifecycle import LifecycleModel, hook


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    password_updated_at = models.DateTimeField(null=True)
    
    @hook('before_update', when='password', has_changed=True)
    def timestamp_password_change(self):
        self.password_updated_at = timezone.now()
```

Instead of overriding `save` and `__init___` in a clunky way that hurts readability:

```python
    # same class and field declarations as above ...
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_password = self.password
        
        
    def save(self, *args, **kwargs):
        if self.pk is not None and self.password != self.__original_password:
            self.password_updated_at = timezone.now()
        super().save(*args, **kwargs)

```

*This is not to say Signals are never useful; my team prefers to use them for incidental concerns not related to the business domain, like cache invalidation.


# Table of Contents:

- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
- [Changelog](#changelog)
- [Testing](#testing)
- [License](#license)

# Installation

```
pip install django-lifecycle
```

# Requirements

* Python (3.3+)
* Django (1.8+)

# Usage 

Either extend the provided abstract base model class:

```python
from django_lifecycle import LifecycleModel, hook


class YourModel(LifecycleModel):
    name = models.CharField(max_length=50)

```

Or add the mixin to your Django model definition:


```python
from django.db import models
from django_lifecycle import LifecycleModelMixin, hook


class YourModel(LifecycleModelMixin, models.Model):
    name = models.CharField(max_length=50)

```

:exclamation: _If you are using **Django 1.8 or below** and want to extend the base model, you also have to add `django_lifecycle` to `INSTALLED_APPS`_.


Great, now we can start adding lifecycle hooks! Let's do a few examples that illustrate the ability to not only hook into certain events, but to add basic conditions that can replace the need for boilerplate conditional code. 

# Changelog <a id="changelog"></a>

## 0.5.0 (September 2019)
* Adds `was_not` condition
* Allow watching changes to FK model field values, not just FK references

## 0.4.2 (July 2019)
* Fixes missing README.md issue that broke install.

## 0.4.1 (June 2019)
* Fixes [urlman](https://github.com/andrewgodwin/urlman)-compatability.

## 0.4.0 (May 2019)
* Fixes `initial_value(field_name)` behavior - should return value even if no change. Thanks @adamJLev!

## 0.3.2 (February 2019)
* Fixes bug preventing hooks from firing for custom PKs. Thanks @atugushev!

## 0.3.1 (August 2018)
* Fixes m2m field bug, in which accessing auto-generated reverse field in `before_create` causes exception b/c PK does not exist yet. Thanks @garyd203!

## 0.3.0 (April 2018)
* Resets model's comparison state for hook conditions after `save` called.

## 0.2.4 (April 2018)
* Fixed support for adding multiple `@hook` decorators to same method.

## 0.2.3 (April 2018)
* Removes residual mixin methods from earlier implementation.

## 0.2.2 (April 2018)
* Save method now accepts `skip_hooks`, an optional boolean keyword argument that controls whether hooked methods are called.

## 0.2.1 (April 2018)
* Fixed bug in `_potentially_hooked_methods` that caused unwanted side effects by accessing model instance methods decorated with `@cache_property` or `@property`. 

## 0.2.0 (April 2018)
* Added Django 1.8 support. Thanks @jtiai!
* Tox testing added for Python 3.4, 3.5, 3.6 and Django 1.8, 1.11 and 2.0. Thanks @jtiai!

# Testing

Tests are found in a simplified Django project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
