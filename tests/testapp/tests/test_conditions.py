from django.test import TestCase

from django_lifecycle.constants import NotSet
from django_lifecycle.conditions import WhenFieldValueChangesTo
from django_lifecycle.conditions import WhenFieldHasChanged
from django_lifecycle.conditions import WhenFieldValueIsNot
from django_lifecycle.conditions import WhenFieldValueIs
from django_lifecycle.conditions import WhenFieldValueWas
from django_lifecycle.conditions import WhenFieldValueWasNot
from tests.testapp.models import UserAccount


class ChainableConditionsTests(TestCase):
    def test_and_condition(self):
        is_homer = WhenFieldValueIs("first_name", value="Homer")
        is_simpson = WhenFieldValueIs("last_name", value="Simpson")
        is_homer_simpson = is_homer & is_simpson

        homer_simpson = UserAccount(first_name="Homer", last_name="Simpson")
        self.assertTrue(is_homer_simpson(homer_simpson))

        homer_flanders = UserAccount(first_name="Homer", last_name="Flanders")
        self.assertFalse(is_homer_simpson(homer_flanders))

        ned_simpson = UserAccount(first_name="Ned", last_name="Simpson")
        self.assertFalse(is_homer_simpson(ned_simpson))

    def test_or_condition(self):
        is_admin = WhenFieldValueIs("username", value="admin")
        is_superuser = WhenFieldValueIs("username", value="superuser")
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
        condition = WhenFieldValueIs("first_name", value="*")
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.first_name = "Ned"
        self.assertTrue(condition(user_account))

    def test_check_is_now_condition_matching_value_should_pass(self):
        condition = WhenFieldValueIs("first_name", value="Ned")
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.first_name = "Ned"
        self.assertTrue(condition(user_account))

    def test_check_is_now_condition_not_matched_value_should_not_pass(self):
        condition = WhenFieldValueIs("first_name", value="Bart")
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_check_was_not_condition_should_pass_when_not_set(self):
        condition = WhenFieldValueWasNot("first_name", value=NotSet)
        data = self.stub_data
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_not_condition_not_matching_value_should_pass(self):
        condition = WhenFieldValueWasNot("first_name", value="Bart")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_not_condition_matched_value_should_not_pass(self):
        condition = WhenFieldValueWasNot("first_name", value="Homer")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_check_was_condition_wildcard_should_pass(self):
        condition = WhenFieldValueWas("first_name", value="*")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_condition_matching_value_should_pass(self):
        condition = WhenFieldValueWas("first_name", value="Homer")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_check_was_condition_not_matched_value_should_not_pass(self):
        condition = WhenFieldValueWas("first_name", value="Bart")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_is_not_condition_should_pass(self):
        condition = WhenFieldValueIsNot("first_name", value="Ned")

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(condition(user_account))

    def test_is_not_condition_should_not_pass(self):
        condition = WhenFieldValueIsNot("first_name", value="Ned")

        data = self.stub_data
        data["first_name"] = "Ned"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(condition(user_account))

    def test_changes_to_condition_should_pass(self):
        condition = WhenFieldValueChangesTo("last_name", value="Flanders")
        data = self.stub_data
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.last_name = "Flanders"
        self.assertTrue(condition(user_account))

    def test_changes_to_condition_included_in_update_fields_should_fire_hook(self):
        condition = WhenFieldValueChangesTo("last_name", value="Flanders")
        user_account = UserAccount.objects.create(**self.stub_data)
        user_account.last_name = "Flanders"
        self.assertTrue(condition(user_account, update_fields=["last_name"]))

    def test_changes_to_condition_not_included_in_update_fields_should_not_fire_hook(
        self,
    ):
        condition = WhenFieldValueChangesTo("last_name", value="Flanders")
        user_account = UserAccount.objects.create(**self.stub_data)
        user_account.last_name = "Flanders"
        self.assertFalse(condition(user_account, update_fields=["first_name"]))

    def test_changes_to_condition_should_not_pass(self):
        condition = WhenFieldValueChangesTo("last_name", value="Flanders")
        data = self.stub_data
        data["first_name"] = "Marge"
        data["last_name"] = "Simpson"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.last_name = "Bouvier"
        self.assertFalse(condition(user_account))
