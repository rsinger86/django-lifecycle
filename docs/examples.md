# Examples
Here are some examples to illustrate how you can hook into specific lifecycle moments, optionally based on state transitions.

## Specific lifecycle moments

For simple cases, you might always want something to happen at a certain point, such as after saving or before deleting a model instance.
When a user is first created, you could process a thumbnail image in the background and send the user an email:

```python
    @hook(AFTER_CREATE)
    def do_after_create_jobs(self):
        enqueue_job(process_thumbnail, self.picture_url)

        mail.send_mail(
            'Welcome!', 'Thank you for joining.',
            'from@example.com', ['to@example.com'],
        )
```

Or you want to email a user when their account is deleted. You could add the decorated method below:

```python
    @hook(AFTER_DELETE)
    def email_deleted_user(self):
        mail.send_mail(
            'We have deleted your account', 'We will miss you!.',
            'customerservice@corporate.com', ['human@gmail.com'],
        )
```

Or if you want to enqueue a background job that depends on state being committed to your database

```python
@hook(AFTER_CREATE, on_commit=True)
def do_after_create_jobs(self):
    enqueue_job(send_item_shipped_notication, self.item_id)
```

Read on to see how to only fire the hooked method if certain conditions about the model's current and previous state are met.

## Transitions between specific values

Maybe you only want the hooked method to run under certain circumstances related to the state of your model. If a model's `status` field change from `"active"` to `"banned"`, you may want to send an email to the user:

```python
@hook(
    AFTER_UPDATE, 
    condition=(
        WhenFieldValueWas("status", value="active") 
        & WhenFieldValueIs('status', value='banned')
    )
)
def email_banned_user(self):
    mail.send_mail(
        'You have been banned', 'You may or may not deserve it.',
        'communitystandards@corporate.com', ['mr.troll@hotmail.com'],
    )
``` 

The `WhenFieldValueWas` and `WhenFieldValueIs` conditions allow you to compare the model's state from when it was first instantiated to the current moment. You can also pass `"*"` to indicate any value - these are the defaults, meaning that by default the hooked method will fire. 

## Preventing state transitions

You can also enforce certain disallowed transitions. For example, maybe you don't want your staff to be able to delete an active trial because they should expire instead:

```python
@hook(BEFORE_DELETE, condition=WhenFieldValueIs("has_trial", value=True))
def ensure_trial_not_active(self):
    raise CannotDeleteActiveTrial('Cannot delete trial user!')
```

## Any change to a field

You can use the `WhenFieldValueChangesTo` condition to run the hooked method if a field has changed.

```python
@hook(BEFORE_UPDATE, condition=WhenFieldHasChanged("address", has_changed=True))
def timestamp_address_change(self):
    self.address_updated_at = timezone.now()
```

## When a field's value is NOT

You can have a hooked method fire when a field's value IS NOT equal to a certain value.

```python
@hook(BEFORE_SAVE, condition=WhenFieldValueIsNot("email", value=None))
def lowercase_email(self):
    self.email = self.email.lower()
```

## When a field's value was NOT

You can have a hooked method fire when a field's initial value was not equal to a specific value.

```python
@hook(
    BEFORE_SAVE, 
    condition=(
        WhenFieldValueWasNot("status", value="rejected") 
        & WhenFieldValueIs("status", value="published")
    )
)
def send_publish_alerts(self):
    send_mass_email()
```

## When a field's value changes to

You can have a hooked method fire when a field's initial value was not equal to a specific value
but now is.

```python
    @hook(BEFORE_SAVE, condition=WhenFieldValueChangesTo("status", value="published"))
    def send_publish_alerts(self):
        send_mass_email()
```

Generally, `WhenFieldValueChangesTo` is a shorthand for the situation when `WhenFieldValueWasNot` and `WhenFieldValueIs` 
conditions have the same value. The sample above is equal to:

```python
@hook(
    BEFORE_SAVE, 
    condition=(
        WhenFieldValueWasNot("status", value="published")
        & WhenFieldValueIs("status", value="published")
    )
)
def send_publish_alerts(self):
    send_mass_email()
```

## Stacking decorators

You can decorate the same method multiple times if you want to hook a method to multiple moments.

```python
@hook(AFTER_UPDATE, condition=WhenFieldHasChanged("published", has_changed=True))
@hook(AFTER_CREATE, condition=WhenFieldHasChanged("type", has_changed=True))
def handle_update(self):
    # do something
```

## Going deeper with utility methods

If you need to hook into events with more complex conditions, you can [write your own conditions](advanced.md), or take advantage of `has_changed` and `initial_value` [utility methods](advanced.md):

```python
@hook(AFTER_UPDATE)
def on_update(self):
    if self.has_changed('username') and not self.has_changed('password'):
        # do the thing here
        if self.initial_value('login_attempts') == 2:
            do_thing()
        else:
            do_other_thing()
```

