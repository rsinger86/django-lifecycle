# Advanced Usage

## Utility Methods <a id="utility-method-doc"></a>

These are available on your model instance when the mixin or extend the base model is used.

| Method       | Details |
|:-------------:|:-------------:|
| `has_changed(field_name: str) -> bool` | Return a boolean indicating whether the field's value has changed since the model was initialized |
| `initial_value(field_name: str) -> bool` | Return the value of the field when the model was first initialized |

### Example
You can use these methods for more advanced checks, for example:

```python
from django_lifecycle import LifecycleModel, AFTER_UPDATE, hook


class UserAccount(LifecycleModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    marital_status = models.CharField(max_length=100)

    @hook(AFTER_UPDATE)
    def on_name_change_heck_on_marietal_status(self):
        if self.has_changed('last_name') and not self.has_changed('marietal_status'):
            send_mail(to=self.email, "Has your marietal status changed recently?")

```

## Suppressing Hooked Methods <a id="suppressing"></a>

To prevent the hooked methods from being called, pass `skip_hooks=True` when calling save:

```python
   account.save(skip_hooks=True)
```