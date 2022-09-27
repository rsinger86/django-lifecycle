# Django Lifecycle Hooks

[![Package version](https://badge.fury.io/py/django-lifecycle.svg)](https://pypi.python.org/pypi/django-lifecycle)
[![Python versions](https://img.shields.io/pypi/status/django-lifecycle.svg)](https://img.shields.io/pypi/status/django-lifecycle.svg/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-lifecycle.svg)](https://pypi.org/project/django-lifecycle/)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-lifecycle)

This project provides a `@hook` decorator as well as a base model and mixin to add lifecycle hooks to your Django models. Django's built-in approach to offering lifecycle hooks is [Signals](https://docs.djangoproject.com/en/dev/topics/signals/). However, my team often finds that Signals introduce unnecessary indirection and are at odds with Django's "fat models" approach.

**Django Lifecycle Hooks** supports Python 3.7 to 3.10, Django 2.x, 3.x, and 4.x

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

## 1.0.0 (May 2022)

- Drops Python 3.6 support
- Adds `priority` hook kwarg to control the order in which hooked methods fire. Thanks @EnriqueSoria!
- Internal cleanup/refactoring. Thanks @EnriqueSoria!

## 0.9.6 (February 2022)

- Adds missing `packaging` to `install_requires`. Thanks @mikedep333!

## 0.9.5 (February 2022)

- Makes the `has_changed`, `changes_to` conditions depend on whether the field in question was included in the SQL update/insert statement by checking
  the `update_fields` argument passed to save.

## 0.9.4 (February 2022)

- Adds optional @hook `on_commit` argument for executing hooks when the database transaction is committed. Thanks @amcclosky!

## 0.9.3 (October 2021)

- Correct packge info to note that Django 3.2 is supported.

## 0.9.2 (October 2021)

- Run hooked methods inside transactions, just as signals do. Thanks @amirmotlagh!

## 0.9.1 (March 2021)

- Makes hooks work with OneToOneFields. Thanks @bahmdev!

## 0.9.0 (February 2021)

- Prevents calling a hooked method twice with the same state. Thanks @garyd203!

## 0.8.1 (January 2021)

- Added missing return to `delete()` method override. Thanks @oaosman84!

## 0.8.0 (October 2020)

- Significant performance improvements. Thanks @dralley!

## 0.7.7 (August 2020)

- Fixes issue with `GenericForeignKey`. Thanks @bmbouter!

## 0.7.6 (May 2020)

- Updates to use constants for hook names; updates docs to indicate Python 3.8/Django 3.x support. Thanks @thejoeejoee!

## 0.7.5 (April 2020)

- Adds static typed variables for hook names; thanks @Faisal-Manzer!
- Fixes some typos in docs; thanks @tomdyson and @bmispelon!

## 0.7.1 (January 2020)

- Fixes bug in `utils._get_field_names` that could cause recursion bug in some cases.

## 0.7.0 (December 2019)

- Adds `changes_to` condition - thanks @samitnuk! Also some typo fixes in docs.

## 0.6.1 (November 2019)

- Remove variable type annotation for Python 3.5 compatability.

## 0.6.0 (October 2019)

- Adds `when_any` hook parameter to watch multiple fields for state changes

## 0.5.0 (September 2019)

- Adds `was_not` condition
- Allow watching changes to FK model field values, not just FK references

## 0.4.2 (July 2019)

- Fixes missing README.md issue that broke install.

## 0.4.1 (June 2019)

- Fixes [urlman](https://github.com/andrewgodwin/urlman)-compatability.

## 0.4.0 (May 2019)

- Fixes `initial_value(field_name)` behavior - should return value even if no change. Thanks @adamJLev!

## 0.3.2 (February 2019)

- Fixes bug preventing hooks from firing for custom PKs. Thanks @atugushev!

## 0.3.1 (August 2018)

- Fixes m2m field bug, in which accessing auto-generated reverse field in `before_create` causes exception b/c PK does not exist yet. Thanks @garyd203!

## 0.3.0 (April 2018)

- Resets model's comparison state for hook conditions after `save` called.

## 0.2.4 (April 2018)

- Fixed support for adding multiple `@hook` decorators to same method.

## 0.2.3 (April 2018)

- Removes residual mixin methods from earlier implementation.

## 0.2.2 (April 2018)

- Save method now accepts `skip_hooks`, an optional boolean keyword argument that controls whether hooked methods are called.

## 0.2.1 (April 2018)

- Fixed bug in `_potentially_hooked_methods` that caused unwanted side effects by accessing model instance methods decorated with `@cache_property` or `@property`.

## 0.2.0 (April 2018)

- Added Django 1.8 support. Thanks @jtiai!
- Tox testing added for Python 3.4, 3.5, 3.6 and Django 1.8, 1.11 and 2.0. Thanks @jtiai!

# Testing

Tests are found in a simplified Django project in the `/tests` folder. Install the project requirements and do `./manage.py test` to run them.

# License

See [License](LICENSE.md).
