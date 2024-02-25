from django.test import TestCase

from django_lifecycle import NotSet
from django_lifecycle.conditions import WhenFieldChangesTo
from django_lifecycle.conditions import WhenFieldHasChanged
from django_lifecycle.conditions import WhenFieldIsNot
from django_lifecycle.conditions import WhenFieldIsNow
from django_lifecycle.conditions import WhenFieldWas
from django_lifecycle.conditions import WhenFieldWasNot
from tests.testapp.models import UserAccount


class ChainableConditionsTests(TestCase):
    def test_and_condition(self):
        is_homer = WhenFieldIsNow("first_name", is_now="Homer")
        is_simpson = WhenFieldIsNow("last_name", is_now="Simpson")
        is_homer_simpson = is_homer & is_simpson

        homer_simpson = UserAccount(first_name="Homer", last_name="Simpson")
        self.assertTrue(is_homer_simpson(homer_simpson))

        homer_flanders = UserAccount(first_name="Homer", last_name="Flanders")
        self.assertFalse(is_homer_simpson(homer_flanders))

        ned_simpson = UserAccount(first_name="Ned", last_name="Simpson")
        self.assertFalse(is_homer_simpson(ned_simpson))

    def test_or_condition(self):
        is_admin = WhenFieldIsNow("username", is_now="admin")
        is_superuser = WhenFieldIsNow("username", is_now="superuser")
        user_has_superpowers = is_admin | is_superuser

        self.assertTrue(user_has_superpowers(UserAccount(username="admin")))
        self.assertTrue(user_has_superpowers(UserAccount(username="superuser")))
        self.assertFalse(user_has_superpowers(UserAccount(username="citizen")))


class ConditionsTests(TestCase):
    @property
    def stub_data(self):
        return {
            "username": "homer.simpson",
            "first_name": "Homer",
            "last_name": "Simpson",
            "password": "donuts",
        }

    def test_has_changed_specs(self):
        condition = WhenFieldHasChanged("first_name", has_changed=True)

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()

        self.assertFalse(condition(user_account))
        user_account.first_name = "Ned"
        self.assertTrue(condition(user_account))

    def test_check_is_now_condition_wildcard_should_pass(self):
        condition = WhenFieldIsNow("first_name", is_now="*")
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.first_name = "Ned"
        self.assertTrue(condition(user_account))

    def test_check_is_now_condition_matching_value_should_pass(self):
        condition = WhenFieldIsNow("first_name", is_now="Ned")
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.first_name = "Ned"
        self.assertTrue(condition(user_account))

    def test_check_is_now_condition_not_matched_value_should_not_pass(self):
        condition = WhenFieldIsNow("first_name", is_now="Bart")
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_check_was_not_condition_should_pass_when_not_set(self):
        condition = WhenFieldWasNot("first_name", was_not=NotSet)
        data = self.stub_data
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_not_condition_not_matching_value_should_pass(self):
        condition = WhenFieldWasNot("first_name", was_not="Bart")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_not_condition_matched_value_should_not_pass(self):
        condition = WhenFieldWasNot("first_name", was_not="Homer")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_check_was_condition_wildcard_should_pass(self):
        condition = WhenFieldWas("first_name", was="*")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_condition_matching_value_should_pass(self):
        condition = WhenFieldWas("first_name", was="Homer")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_condition_not_matched_value_should_not_pass(self):
        condition = WhenFieldWas("first_name", was="Bart")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_is_not_condition_should_pass(self):
        condition = WhenFieldIsNot("first_name", is_not="Ned")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_is_not_condition_should_not_pass(self):
        condition = WhenFieldIsNot("first_name", is_not="Ned")

        data = self.stub_data
        data["first_name"] = "Ned"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_changes_to_condition_should_pass(self):
        condition = WhenFieldChangesTo("last_name", changes_to="Flanders")
        data = self.stub_data
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.last_name = "Flanders"
        self.assertTrue(condition(user_account))

    def test_changes_to_condition_included_in_update_fields_should_fire_hook(self):
        condition = WhenFieldChangesTo("last_name", changes_to="Flanders")
        user_account = UserAccount.objects.create(**self.stub_data)
        user_account.last_name = "Flanders"
        self.assertTrue(condition(user_account, update_fields=["last_name"]))

    def test_changes_to_condition_not_included_in_update_fields_should_not_fire_hook(
        self,
    ):
        condition = WhenFieldChangesTo("last_name", changes_to="Flanders")
        user_account = UserAccount.objects.create(**self.stub_data)
        user_account.last_name = "Flanders"
        self.assertFalse(condition(user_account, update_fields=["first_name"]))

    def test_changes_to_condition_should_not_pass(self):
        condition = WhenFieldChangesTo("last_name", changes_to="Flanders")
        data = self.stub_data
        data["first_name"] = "Marge"
        data["last_name"] = "Simpson"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.last_name = "Bouvier"
        self.assertFalse(condition(user_account))
