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

Read on to see how to only fire the hooked method if certain conditions about the model's current and previous state are met.

## Transitions between specific values

Maybe you only want the hooked method to run under certain circumstances related to the state of your model. If a model's `status` field change from `"active"` to `"banned"`, you may want to send an email to the user:

```python
    @hook(AFTER_UPDATE, when='status', was='active', is_now='banned')
    def email_banned_user(self):
        mail.send_mail(
            'You have been banned', 'You may or may not deserve it.',
            'communitystandards@corporate.com', ['mr.troll@hotmail.com'],
        )
``` 

The `was` and `is_now` keyword arguments allow you to compare the model's state from when it was first instantiated to the current moment. You can also pass `"*"` to indicate any value - these are the defaults, meaning that by default the hooked method will fire. The `when` keyword specifies which field to check against. 

## Preventing state transitions

You can also enforce certain disallowed transitions. For example, maybe you don't want your staff to be able to delete an active trial because they should expire instead:

```python
    @hook(BEFORE_DELETE, when='has_trial', is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial('Cannot delete trial user!')
```

We've omitted the `was` keyword meaning that the initial state of the `has_trial` field can be any value ("*").

## Any change to a field

You can pass the keyword argument `has_changed=True` to run the hooked method if a field has changed.

```python
    @hook(BEFORE_UPDATE, when='address', has_changed=True)
    def timestamp_address_change(self):
        self.address_updated_at = timezone.now()
```

## When a field's value is NOT

You can have a hooked method fire when a field's value IS NOT equal to a certain value.

```python
    @hook(BEFORE_SAVE, when='email', is_not=None)
    def lowercase_email(self):
        self.email = self.email.lower()
```

## When a field's value was NOT

You can have a hooked method fire when a field's initial value was not equal to a specific value.

```python
    @hook(BEFORE_SAVE, when='status', was_not="rejected", is_now="published")
    def send_publish_alerts(self):
        send_mass_email()
```

## When a field's value changes to

You can have a hooked method fire when a field's initial value was not equal to a specific value
but now is.

```python
    @hook(BEFORE_SAVE, when='status', changes_to="published")
    def send_publish_alerts(self):
        send_mass_email()
```

Generally, `changes_to` is a shorthand for the situation when `was_not` and `is_now` have the
same value. The sample above is equal to:

```python
    @hook(BEFORE_SAVE, when='status', was_not="published", is_now="published")
    def send_publish_alerts(self):
        send_mass_email()
```

## Stacking decorators

You can decorate the same method multiple times if you want to hook a method to multiple moments.

```python
    @hook(AFTER_UPDATE, when="published", has_changed=True)
    @hook(AFTER_CREATE, when="type", has_changed=True)
    def handle_update(self):
        # do something
```

## Watching multiple fields

If you want to hook into the same moment, but base its conditions on multiple fields, you can use the `when_any` parameter.

```python
    @hook(BEFORE_SAVE, when_any=['status', 'type'], has_changed=True)
    def do_something(self):
        # do something
```

## Going deeper with utility methods

If you need to hook into events with more complex conditions, you can take advantage of `has_changed` and `initial_value` [utility methods](advanced.md):

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

