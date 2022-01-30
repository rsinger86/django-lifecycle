import datetime

from django.core import mail
from django.test import TestCase

from django_capture_on_commit_callbacks import capture_on_commit_callbacks

from tests.testapp.models import CannotDeleteActiveTrial, Organization, UserAccount


class UserAccountTestCase(TestCase):
    @property
    def stub_data(self):
        return {
            "username": "homer.simpson",
            "first_name": "Homer",
            "last_name": "Simpson",
            "password": "donuts",
        }

    def test_update_joined_at_before_create(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.refresh_from_db()
        self.assertTrue(isinstance(account.joined_at, datetime.datetime))

    def test_send_welcome_email_after_create(self):
        with capture_on_commit_callbacks(execute=True) as callbacks:
            UserAccount.objects.create(**self.stub_data)
        
        self.assertEquals(len(callbacks), 1, msg=f"{callbacks}")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome!")

    def test_email_banned_user_after_update(self):
        account = UserAccount.objects.create(status="active", **self.stub_data)
        account.refresh_from_db()
        mail.outbox = []
        account.status = "banned"
        account.save()
        self.assertEqual(mail.outbox[0].subject, "You have been banned")

    def test_update_password_updated_at_during_update(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.refresh_from_db()
        account.password = "maggie"
        account.save()
        account.refresh_from_db()

        self.assertTrue(isinstance(account.password_updated_at, datetime.datetime))

    def test_ensure_trial_not_active_before_delete(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.has_trial = True
        account.save()
        self.assertRaises(CannotDeleteActiveTrial, account.delete)

    def test_email_after_delete(self):
        account = UserAccount.objects.create(**self.stub_data)
        mail.outbox = []
        account.delete()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "We have deleted your account")

    def test_only_call_hook_once(self):
        account = UserAccount.objects.create(**self.stub_data)
        account.first_name = "Waylon"
        account.last_name = "Smithers"
        account.save()
        self.assertEqual(account.name_changes, 1)

    def test_lowercase_email(self):
        data = self.stub_data
        data["email"] = "Homer.Simpson@SpringfieldNuclear.com"
        account = UserAccount.objects.create(**data)
        self.assertEqual(account.email, "homer.simpson@springfieldnuclear.com")

    def test_notify_org_name_change(self):
        org = Organization.objects.create(name="Hogwarts")
        UserAccount.objects.create(**self.stub_data, organization=org)
        mail.outbox = []

        account = UserAccount.objects.get()

        with capture_on_commit_callbacks(execute=True) as callbacks:
            org.name = "Coursera Wizardry"
            org.save()

            account.save()
        
        self.assertEquals(len(callbacks), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "The name of your organization has changed!"
        )

    def test_no_notify_sent_if_org_name_has_not_changed(self):
        org = Organization.objects.create(name="Hogwarts")
        UserAccount.objects.create(**self.stub_data, organization=org)
        mail.outbox = []
        account = UserAccount.objects.get()
        account.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_additional_notify_sent_for_specific_org_name_change(self):
        org = Organization.objects.create(name="Hogwarts")
        UserAccount.objects.create(**self.stub_data, organization=org)

        mail.outbox = []

        with capture_on_commit_callbacks(execute=True) as callbacks:
            account = UserAccount.objects.get()

            org.name = "Hogwarts Online"
            org.save()

            account.save()

        self.assertEquals(len(callbacks), 1, msg="Only one hook should be an on_commit callback")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[1].subject, "The name of your organization has changed!"
        )
        self.assertEqual(mail.outbox[0].subject, "You were moved to our online school!")

    def test_email_user_about_name_change(self):
        account = UserAccount.objects.create(**self.stub_data)
        mail.outbox = []
        account.first_name = "Homer the Great"
        account.save()
        self.assertEqual(
            mail.outbox[0].body, "You changed your first name or your last name"
        )

    def test_does_not_email_user_about_name_change_when_name_excluded_from_update_fields(self):
        account = UserAccount.objects.create(**self.stub_data)
        mail.outbox = []
        account.first_name = "Homer the Great"
        account.password = "New password!"

        old_password_updated_at = account.password_updated_at
        account.save(update_fields=["password"])
        self.assertEqual(len(mail.outbox), 0)  # `first_name` change was skipped (as a hook).
        self.assertNotEqual(account.password_updated_at, old_password_updated_at)  # Ensure the other hook is fired.

    def test_emails_user_about_name_change_when_one_field_from_update_fields_intersects_with_condition(self):
        account = UserAccount.objects.create(**self.stub_data)
        mail.outbox = []
        account.first_name = "Homer the Great"
        account.password = "New password!"

        old_password_updated_at = account.password_updated_at
        account.save(update_fields=["first_name", "password"])
        self.assertEqual(
            mail.outbox[0].body, "You changed your first name or your last name"
        )
        self.assertNotEqual(account.password_updated_at, old_password_updated_at)  # Both hooks fired.

    def test_empty_update_fields_does_not_fire_any_hooks(self):
        # In Django, an empty list supplied to `update_fields` means not updating any field.
        account = UserAccount.objects.create(**self.stub_data)
        mail.outbox = []
        account.first_name = "Flanders"
        account.password = "new pass"

        old_password_updated_at = account.password_updated_at
        account.save(update_fields=[])
        # Did not raise, so last name hook didn't fire.
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(account.password_updated_at, old_password_updated_at)  # Password hook didn't fire either.

    def test_skip_hooks(self):
        """
        Hooked method that auto-lowercases email should be skipped.
        """
        account = UserAccount.objects.create(**self.stub_data)
        account.email = "Homer.Simpson@springfieldnuclear"
        account.save(skip_hooks=True)
        self.assertEqual(account.email, "Homer.Simpson@springfieldnuclear")

    def test_delete_should_return_default_django_value(self):
        """
        Hooked method that auto-lowercases email should be skipped.
        """
        UserAccount.objects.create(**self.stub_data)
        value = UserAccount.objects.all().delete()

        self.assertEqual(value, (1, {"testapp.UserAccount": 1}))
