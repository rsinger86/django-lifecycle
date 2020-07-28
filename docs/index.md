# Django Lifecycle Hooks

[![Package version](https://badge.fury.io/py/django-lifecycle.svg)](https://pypi.python.org/pypi/django-lifecycle)
[![Python versions](https://img.shields.io/pypi/status/django-lifecycle.svg)](https://img.shields.io/pypi/status/django-lifecycle.svg/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-lifecycle.svg)](https://pypi.org/project/django-lifecycle/)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-lifecycle)


This project provides a `@hook` decorator as well as a base model and mixin to add lifecycle hooks to your Django models. Django's built-in approach to offering lifecycle hooks is [Signals](https://docs.djangoproject.com/en/dev/topics/signals/). However, my team often finds that Signals introduce unnecessary indirection and are at odds with Django's "fat models" approach.

In short, you can write model code like this:

```python
from django_lifecycle import LifecycleModel, hook, BEFORE_UPDATE, AFTER_UPDATE


class Article(LifecycleModel):
    contents = models.TextField()
    updated_at = models.DateTimeField(null=True)
    status = models.ChoiceField(choices=['draft', 'published'])
    editor = models.ForeignKey(AuthUser)

    @hook(BEFORE_UPDATE, when='contents', has_changed=True)
    def on_content_change(self):
        self.updated_at = timezone.now()

    @hook(AFTER_UPDATE, when="status", was="draft", is_now="published")
    def on_publish(self):
        send_email(self.editor.email, "An article has published!")
```

Instead of overriding `save` and `__init__` in a clunky way that hurts readability:

```python
    # same class and field declarations as above ...

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._orig_contents = self.contents
        self._orig_status = self.status


    def save(self, *args, **kwargs):
        if self.pk is not None and self.contents != self._orig_contents):
            self.updated_at = timezone.now()

        super().save(*args, **kwargs)

        if self.status != self._orig_status:
            send_email(self.editor.email, "An article has published!")
```

## Requirements

* Python (3.3+)
* Django (1.8+)

## Installation

```
pip install django-lifecycle
```

## Getting Started

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

If you are using **Django 1.8 or below** and want to extend the base model, you also have to add `django_lifecycle` to `INSTALLED_APPS`.

[Read on](examples.md) to see more examples of how to use lifecycle hooks.
