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
- [Examples](#examples)
  - [Simple Hook - No Conditions](#ex-simple-hook)
  - [Hook with Transition Conditions: Part I](#ex-condition-hook-1")
  - [Hook with Transition Conditions: Part II](#ex-condition-hook-2")
  - [Hook with Simple Change Condition](#ex-simple-change)
  - [Hook with "Is Not" Condition](#ex-is-not)
  - [Custom Condition](#ex-custom-condition)
  - [Multiple decorators, Same Method](#ex-multiple-decorators)
  - [Watching Changes to Foreign Key Fields](#watching-changes-to-foreign-key-fields)
    - [FK Reference Changes](#fk-changes)
    - [FK Model Field Changes](#fk-model-field-changes)
- [Documentation](#docs)
  - [Lifecycle Hook](#lifecycle-hooks-doc)
  - [Condition Arguments](#condition-args-doc)
  - [Utility Methods](#utility-method-doc)
  - [Suppressing Hooked Methods](#suppressing)
  - [Limitations](#limitations)
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

# Examples

## Simple Hook - No conditions <a id="ex-simple-hook"></a>

Say you want to process a thumbnail image in the background and send the user an email when they first sign up:

```python
    @hook('after_create')
    def do_after_create_jobs(self):
        enqueue_job(process_thumbnail, self.picture_url)

        mail.send_mail(
            'Welcome!', 'Thank you for joining.',
            'from@example.com', ['to@example.com'],
        )
```

Or say you want to email a user when their account is deleted. You could add the decorated method below:

```python
    @hook('after_delete')
    def email_deleted_user(self):
        mail.send_mail(
            'We have deleted your account', 'Thank you for your time.',
            'customerservice@corporate.com', ['human@gmail.com'],
        )
```

## Hook with Transition Conditions: Part I <a id="ex-condition-hook-1"></a>

Maybe you only want the hooked method to run only under certain circumstances related to the state of your model. Say if updating a model instance changes a "status" field's value from "active" to "banned", you want to send them an email:

```python
    @hook('after_update', when='status', was='active', is_now='banned')
    def email_banned_user(self):
        mail.send_mail(
            'You have been banned', 'You may or may not deserve it.',
            'communitystandards@corporate.com', ['mr.troll@hotmail.com'],
        )
``` 

The `was` and `is_now` keyword arguments allow you to compare the model's state from when it was first instantiated to the current moment. You can also pass an `*` to indicate any value - these are the defaults, meaning that by default the hooked method will fire. The `when` keyword specifies which field to check against. 

## Hook with Transition Conditions: Part II <a id="ex-condition-hook-2"></a>

You can also enforce certain dissallowed transitions. For example, maybe you don't want your staff to be able to delete an active trial because they should always expire:

```python
    @hook('before_delete', when='has_trial', is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial('Cannot delete trial user!')
```

We've ommitted the `was` keyword meaning that the initial state of the `has_trial` field can be any value ("*").

## Hook with Simple Change Condition <a id="ex-simple-change"></a>

As we saw in the very first example, you can also pass the keyword argument `has_changed=True` to run the hooked method if a field has changed, regardless of previous or current value.

```python
    @hook('before_update', when='address', has_changed=True)
    def timestamp_address_change(self):
        self.address_updated_at = timezone.now()
```

## Hook with "Is Not" Condition <a id="ex-is-not"></a>

You can also have a hooked method fire when a field's value IS NOT equal to a certain value. See a common example below involving lowercasing a user's email. 

```python
    @hook('before_save', when='email', is_not=None)
    def lowercase_email(self):
        self.email = self.email.lower()
```

## Custom Condition <a id="ex-custom-condition"></a>

If you need to hook into events with more complex conditions, you can take advantage of `has_changed` and `initial_value` methods:

 ```python
    @hook('after_update')
    def on_update(self):
        if self.has_changed('username') and not self.has_changed('password'):
            # do the thing here
            if self.initial_value('login_attempts') == 2:
                do_thing()
            else:
                do_other_thing()
```

## Multiple decorators, Same Method <a id="ex-multiple-decorators"></a>

You can decorate the same method multiple times if you want. 

```python
    @hook('after_create')
    @hook('after_delete')
    def db_rows_changed(self):
        do_something()
```

## Watching Changes to Foreign Key Fields<a id="check-fk-values"></a>

### FK Changes

You can watch whether a foriegn key reference changes by putting the name of the FK field in the `when` parameter:

```python
class Organization(models.Model):
    name = models.CharField(max_length=100)


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=600)
    employer = models.ForeignKey(Organization, on_delete=models.SET_NULL)

    @hook("after_update", when="employer", has_changed=True)
    def notify_user_of_employer_change(self):
        mail.send_mail("Update", "You now work for someone else!", [self.email])
```

To be clear: This hook will fire when the value in the database column that stores the foreign key (in this case, `organization_id`) changes. Read on to see how to watch for changes to *fields on the related model*.

### FK Model Field Changes
You can have a hooked method fire based on the *value of a field* on a foreign key-related model using dot notation:

```python
class Organization(models.Model):
    name = models.CharField(max_length=100)


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=600)
    employer = models.ForeignKey(Organization, on_delete=models.SET_NULL)

    @hook("after_update", when="employer.name", has_changed=True, is_now="Google")
    def notify_user_of_google_buy_out(self):
        mail.send_mail("Update", "Google bought your employer!", ["to@example.com"],)
```
<a id="fk-hook-warning"></a>
:heavy_exclamation_mark: **If you use dot-notation**.. 
*Please be aware of the potential performance hit*: When your model is first initialized, the related model will be also be loaded in order to store the "initial" state of the related field. Models set up with these hooks should always be loaded using `.select_related()`, i.e. `UserAccount.objects.select_related("organization")` for the example above. If you don't do this, you will almost certainly experience a major [N+1](https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem-in-orm-object-relational-mapping) performance problem.

# Documentation <a id="docs"></a>

## Lifecycle Hooks <a id="lifecycle-hooks-doc"></a>

The hook name is passed as the first positional argument to the @hook decorator, e.g. `@hook('before_create)`.

`@hook(hook_name: str, **kwargs)`


| Hook name       | When it fires   |
|:-------------:|:-------------:|
| before_save | Immediately before `save` is called |
| after_save | Immediately after `save` is called
| before_create | Immediately before `save` is called, if `pk` is `None` |
| after_create | Immediately after `save` is called, if `pk` was initially `None` |
| before_update | Immediately before `save` is called, if `pk` is NOT `None` |
| after_update | Immediately after `save` is called, if `pk` was NOT `None` |
| before_delete | Immediately before `delete` is called |
| after_delete | Immediately after `delete` is called |


## Condition Arguments <a id="condition-args-doc"></a>

`@hook(hook_name: str, when: str = None, was='*', is_now='*', has_changed: bool = None, is_not = None, was_not = None):`

| Keywarg arg       | Type   | Details |
|:-------------:|:-------------:|:-------------:|
| when | str | The name of the field that you want to check against; required for the conditions below to be checked. Use the name of a FK field to watch changes to the related model *reference* or use dot-notation to watch changes to the *values* of fields on related models, e.g. `"organization.name"`. But [please be aware](#fk-hook-warning) of potential performance drawbacks. |
| has_changed | bool | Only fire the hooked method if the value of the `when` field has changed since the model was initialized  |
| is_now | any | Only fire the hooked method if the value of the `when` field is currently equal to this value; defaults to `*`.  |
| is_not | any | Only fire the hooked method if the value of the `when` field is NOT equal to this value  |
| was | any | Only fire the hooked method if the value of the `when` field was equal to this value when first initialized; defaults to `*`.  |
| was_not | any | Only fire the hooked method if the value of the `when` field was NOT equal to this value when first initialized. |


## Utility Methods <a id="utility-method-doc"></a>

These are available on your model when you use the mixin or extend the base model.

| Method       | Details |
|:-------------:|:-------------:|
| `has_changed(field_name: str) -> bool` | Return a boolean indicating whether the field's value has changed since the model was initialized |
| `initial_value(field_name: str) -> bool` | Return the value of the field when the model was first initialized |

## Suppressing Hooked Methods <a id="suppressing"></a>

To prevent the hooked methods from being called, pass `skip_hooks=True` when calling save:

```python
   account.save(skip_hooks=True)
```

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
