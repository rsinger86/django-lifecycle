## Intro

This project provides a `@hook` decorator as well as a base model or mixin to add lifecycle hooks to your Django models. Django's built-in approach to offering lifecycle hooks is [Signals](https://docs.djangoproject.com/en/2.0/topics/signals/), however in the projects I've worked on, my teams often find that *Signals introduce unnesseary indirection and are at odds with Django's "fat models" approach to including related logic in the model class itself. 

In short, you can write model code that looks like this:

```
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

```
    ### ... previous class and field declaration ...
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_password = self.password
        
        
    def save(self, *args, **kwargs):
        if self.pk is not None and self.password != self.__orginal_password:
            self.password_updated_at = timezone.now()
        super().save(*args, **kwargs)

```

*This is not to say Signals are never useful; my team prefers to use them for incidental concerns not related to the business domain, like cache invalidation.

## Usage 

Either extend the provided abstract base model class:

```
from django_lifecycle import LifecycleModel, hook


class YourModel(LifecycleModel):
    name = models.CharField(max_length=50)

```

Or add the mixin to your Django model definition:


```
from django.db import models
from django_lifecycle import LifecycleModel, hook


class YourModel(LifecycleModelMixin, models.Model):
    name = models.CharField(max_length=50)

```

Great, now we can start adding lifecycle hooks! Let's do a few examples that illustrate the ability to not only hook into certain events, but to add basic conditions that can replace the need for boilerplate conditional code. 

## Example - Simple Hook - No conditions

Say you want to process a thumbnail image in the background and send the user an email when they first sign up:

```
    @hook('after_create')
    def do_after_create_jobs(self):
        enqueue_job(process_thumbnail, self.picture_url)

        mail.send_mail(
            'Welcome!', 'Thank you for joining.',
            'from@example.com', ['to@example.com'],
        )
```

Or say you want to email a user when their account is deleted. You could add the decorated method below:

```
    @hook('after_delete')
    def email_deleted_user(self):
        mail.send_mail(
            'We have deleted your account', 'Thank you for your time.',
            'customerservice@corporate.com', ['human@gmail.com'],
        )
```

## Example - Hook with State Transition Conditions: Part I

Maybe you only want the hooked method to run only under certain circumstances related to the state of your model. Say if updating a model instance changes a "status" field's value from "active" to "banned", you want to send them an email:

```
    @hook('after_update', when='status', was='active', is_now='banned')
    def email_banned_user(self):
        mail.send_mail(
            'You have been banned', 'You may or may not deserve it.',
            'communitystandards@corporate.com', ['mr.troll@hotmail.com'],
        )
``` 

The `was` and `is_now` keyword arguments allow you to compare the model's state from when it was first instantiated to the current moment. You can also pass an `*` to indicate any value - these are the defaults, meaning that by default the hooked method will fire. The `when` keyword specifies which field to check against. 

## Example - Hook with State Transition Conditions: Part II

You can also enforce certain dissallowed transitions. For example, maybe you don't want your staff to be able to delete an active trials because they should expire:

```
    @hook('before_delete', when='has_trial', is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial('Cannot delete trial user!')
```

We've ommitted the `was` keyword meaning that the initial state of the `has_trial` field can be any value ("*").