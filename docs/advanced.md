# Advanced Usage

## Utility Methods <a id="utility-method-doc"></a>

These are available on your model instance when the mixin or extend the base model is used.

|                  Method                  |                                              Details                                              |
|:----------------------------------------:|:-------------------------------------------------------------------------------------------------:|
|  `has_changed(field_name: str) -> bool`  | Return a boolean indicating whether the field's value has changed since the model was initialized |
| `initial_value(field_name: str) -> bool` |                Return the value of the field when the model was first initialized                 |

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
    def on_name_change_heck_on_marital_status(self):
        if self.has_changed('last_name') and not self.has_changed('marital_status'):
            send_mail(to=self.email, "Has your marital status changed recently?")

```

## Custom conditions <a id="custom-conditions"></a>
Custom conditions can be created as long as they respect condition signature
```python
def changes_to_ned_flanders(instance, update_fields=None):
    ...
```

To allow your custom conditions to be chainable, create a class based condition inheriting `ChainableCondition`.
```python
from django_lifecycle import BEFORE_SAVE
from django_lifecycle.conditions import WhenFieldHasChanged
from django_lifecycle.conditions.base import ChainableCondition


class IsNedFlanders(ChainableCondition):
    def __call__(self, instance, update_fields=None):
        return instance.first_name == "Ned" and instance.last_name == "Flanders"

    
@hook(
    BEFORE_SAVE,
    condition=WhenFieldHasChanged("first_name") & WhenFieldHasChanged("last_name") & IsNedFlanders()
)
def foo():
    ...
```

## Suppressing Hooked Methods <a id="suppressing"></a>

To prevent the hooked methods from being called, pass `skip_hooks=True` when calling save:

```python
   account.save(skip_hooks=True)
```