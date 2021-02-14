# Watching Changes to ForeignKey Fields

## ForeignKey Reference Changes

You can watch whether a foreign key reference changes by putting the name of the FK field in the `when` parameter:

```python
class Organization(models.Model):
    name = models.CharField(max_length=100)


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=600)
    employer = models.ForeignKey(Organization, on_delete=models.SET_NULL)

    @hook(AFTER_UPDATE, when="employer", has_changed=True)
    def notify_user_of_employer_change(self):
        mail.send_mail("Update", "You now work for someone else!", [self.email])
```

To be clear: This hook will fire when the value in the database column that stores the foreign key (in this case, `organization_id`) changes. Read on to see how to watch for changes to *fields on the related model*.

## ForeignKey Field Value Changes
You can have a hooked method fire based on the *value of a field* on a foreign key-related model using dot-notation:

```python
class Organization(models.Model):
    name = models.CharField(max_length=100)


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=600)
    employer = models.ForeignKey(Organization, on_delete=models.SET_NULL)

    @hook(AFTER_UPDATE, when="employer.name", has_changed=True, is_now="Google")
    def notify_user_of_google_buy_out(self):
        mail.send_mail("Update", "Google bought your employer!", ["to@example.com"],)
```
<a id="fk-hook-warning"></a>
**If you use dot-notation**,  *Please be aware of the potential performance hit*: When your model is first initialized, the related model will be also be loaded in order to store the "initial" state of the related field. Models set up with these hooks should always be loaded using `.select_related()`, i.e. `UserAccount.objects.select_related("organization")` for the example above. If you don't do this, you will almost certainly experience a major [N+1](https://stackoverflow.com/questions/97197/what-is-the-n1-selects-problem-in-orm-object-relational-mapping) performance problem.
