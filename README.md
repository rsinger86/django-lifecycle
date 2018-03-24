## Intro

This project provides a `@hook` decorator as well as a base model or mixin to add lifecycle hooks to your Django models. Django's built-in approach to offering lifecycle hooks is [Signals](https://docs.djangoproject.com/en/2.0/topics/signals/), however in the projects I've worked on, my teams often find that Signals introduce unnesseary indirection and are at odds with Django's "fat models" approach to including related logic in the model class itself. 

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
