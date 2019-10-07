# Examples

## A specific lifecycle moment

For simple cases, you always want something to happen - after saving, before deleting - regardless of the model's previous or current state. 
For example, you want to process a thumbnail image in the background and send the user an email when they first sign up:

```python
    @hook('after_create')
    def do_after_create_jobs(self):
        enqueue_job(process_thumbnail, self.picture_url)

        mail.send_mail(
            'Welcome!', 'Thank you for joining.',
            'from@example.com', ['to@example.com'],
        )
```

Or you want to email a user when their account is deleted. You could add the decorated method below:

```python
    @hook('after_delete')
    def email_deleted_user(self):
        mail.send_mail(
            'We have deleted your account', 'Thank you for your time.',
            'customerservice@corporate.com', ['human@gmail.com'],
        )
```

Read on to see how to only fire the hooked method if certain conditions about the model's current and previous state are met.

## A transition btwn specific values

Maybe you only want the hooked method to run only under certain circumstances related to the state of your model. If a model's `status` field change from "active" to "banned", you want to send an email to the user:

```python
    @hook('after_update', when='status', was='active', is_now='banned')
    def email_banned_user(self):
        mail.send_mail(
            'You have been banned', 'You may or may not deserve it.',
            'communitystandards@corporate.com', ['mr.troll@hotmail.com'],
        )
``` 

The `was` and `is_now` keyword arguments allow you to compare the model's state from when it was first instantiated to the current moment. You can also pass an `*` to indicate any value - these are the defaults, meaning that by default the hooked method will fire. The `when` keyword specifies which field to check against. 

## A field's current value is

You can also enforce certain dissallowed transitions. For example, maybe you don't want your staff to be able to delete an active trial because they should always expire:

```python
    @hook('before_delete', when='has_trial', is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial('Cannot delete trial user!')
```

We've ommitted the `was` keyword meaning that the initial state of the `has_trial` field can be any value ("*").

## A field has changed at all

As we saw in the very first example, you can also pass the keyword argument `has_changed=True` to run the hooked method if a field has changed, regardless of previous or current value.

```python
    @hook('before_update', when='address', has_changed=True)
    def timestamp_address_change(self):
        self.address_updated_at = timezone.now()
```

## A field's current value is NOT

You can also have a hooked method fire when a field's value IS NOT equal to a certain value. See a common example below involving lowercasing a user's email. 

```python
    @hook('before_save', when='email', is_not=None)
    def lowercase_email(self):
        self.email = self.email.lower()
```

## Go deeper with utility methods

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