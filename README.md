# Django Lifecycle Hooks

[![Package version](https://badge.fury.io/py/django-lifecycle.svg)](https://pypi.python.org/pypi/django-lifecycle)
[![Python versions](https://img.shields.io/pypi/status/django-lifecycle.svg)](https://img.shields.io/pypi/status/django-lifecycle.svg/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-lifecycle.svg)](https://pypi.org/project/django-lifecycle/)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-lifecycle)

This project provides a `@hook` decorator as well as a base model and mixin to add lifecycle hooks to your Django models. Django's built-in approach to offering lifecycle hooks is [Signals](https://docs.djangoproject.com/en/dev/topics/signals/). However, my team often finds that Signals introduce unnecessary indirection and are at odds with Django's "fat models" approach.

**Django Lifecycle Hooks** supports:

* Python 3.7, 3.8, 3.9, 3.10, 3.11, and 3.12
* Django 2.2, 3.2, 4.0, 4.1, 4.2, and 5.0

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
        if self.pk is not None and self.contents != self._orig_contents:
            self.updated_at = timezone.now()

        super().save(*args, **kwargs)

        if self.status != self._orig_status:
            send_email(self.editor.email, "An article has published!")
```

---

**Documentation**: <a href="https://rsinger86.github.io/django-lifecycle/" target="_blank">https://rsinger86.github.io/django-lifecycle</a>

**Source Code**: <a href="https://github.com/rsinger86/django-lifecycle/" target="_blank">https://github.com/rsinger86/django-lifecycle</a>

---

# Changelog

See [Changelog](CHANGELOG.md)

# Testing

Tests are found in a simplified Django project in the `/tests` folder. Install the project requirements and do `./manage.py test` to run them.

# License

See [License](LICENSE.md).
