from unittest.mock import MagicMock

from django.test import TestCase

from django_lifecycle import NotSet
from tests.testapp.models import CannotRename, Organization, UserAccount


class LifecycleMixinTests(TestCase):
    def setUp(self):
        UserAccount.objects.all().delete()
        Organization.objects.all().delete()

    @property
    def stub_data(self):
        return {
            "username": "homer.simpson",
            "first_name": "Homer",
            "last_name": "Simpson",
            "password": "donuts",
        }

    def test_snapshot_state(self):
        org = Organization.objects.create(name="Dunder Mifflin")
        UserAccount.objects.create(**self.stub_data, organization=org)
        user_account = UserAccount.objects.get()

        state = user_account._snapshot_state()

        self.assertEqual(
            state,
            {
                "id": user_account.id,
                "username": "homer.simpson",
                "first_name": "Homer",
                "last_name": "Simpson",
                "password": "donuts",
                "email": None,
                "password_updated_at": None,
                "joined_at": user_account.joined_at,
                "has_trial": False,
                "organization_id": org.id,
                "status": "active",
                "organization.name": "Dunder Mifflin",
            },
        )

    def test_initial_value_for_fk_model_field(self):
        UserAccount.objects.create(
            **self.stub_data,
            organization=Organization.objects.create(name="Dunder Mifflin")
        )

        user_account = UserAccount.objects.get()
        self.assertEqual(
            user_account.initial_value("organization.name"), "Dunder Mifflin"
        )

    def test_initial_value_if_field_has_changed(self):
        data = self.stub_data
        data["username"] = "Joe"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(user_account.has_changed("username"))
        user_account.username = "Josephine"
        self.assertEqual(user_account.initial_value("username"), "Joe")

    def test_initial_value_if_field_has_not_changed(self):
        data = self.stub_data
        data["username"] = "Joe"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertEqual(user_account.initial_value("username"), "Joe")

    def test_current_value_for_watched_fk_model_field(self):
        org = Organization.objects.create(name="Dunder Mifflin")
        UserAccount.objects.create(**self.stub_data, organization=org)
        user_account = UserAccount.objects.get()

        self.assertEqual(
            user_account._current_value("organization.name"), "Dunder Mifflin"
        )

        org.name = "Dwight's Paper Empire"
        org.save()
        user_account._clear_watched_fk_model_cache()

        self.assertEqual(
            user_account._current_value("organization.name"), "Dwight's Paper Empire"
        )

    def test_run_hooked_methods_for_when(self):
        instance = UserAccount(first_name="Bob")

        instance._potentially_hooked_methods = MagicMock(
            return_value=[
                MagicMock(
                    __name__="method_that_does_fires",
                    _hooked=[
                        {
                            "hook": "after_create",
                            "when": "first_name",
                            "when_any": None,
                            "has_changed": None,
                            "is_now": "Bob",
                            "is_not": NotSet,
                            "was": "*",
                            "was_not": NotSet,
                            "changes_to": NotSet,
                        }
                    ],
                ),
                MagicMock(
                    __name__="method_that_does_not_fire",
                    _hooked=[
                        {
                            "hook": "after_create",
                            "when": "first_name",
                            "when_any": None,
                            "has_changed": None,
                            "is_now": "Bill",
                            "is_not": NotSet,
                            "was": "*",
                            "was_not": NotSet,
                            "changes_to": NotSet,
                        }
                    ],
                ),
            ]
        )
        fired_methods = instance._run_hooked_methods("after_create")
        self.assertEqual(fired_methods, ["method_that_does_fires"])

    def test_run_hooked_methods_for_when_any(self):
        instance = UserAccount(first_name="Bob")

        instance._potentially_hooked_methods = MagicMock(
            return_value = [
                MagicMock(
                    __name__="method_that_does_fires",
                    _hooked=[
                        {
                            "hook": "after_create",
                            "when": None,
                            "when_any": ["first_name", "last_name", "password"],
                            "has_changed": None,
                            "is_now": "Bob",
                            "is_not": NotSet,
                            "was": "*",
                            "was_not": NotSet,
                            "changes_to": NotSet,
                        }
                    ],
                ),
                MagicMock(
                    __name__="method_that_does_not_fire",
                    _hooked=[
                        {
                            "hook": "after_create",
                            "when": "first_name",
                            "when_any": None,
                            "has_changed": None,
                            "is_now": "Bill",
                            "is_not": NotSet,
                            "was": "*",
                            "was_not": NotSet,
                            "changes_to": NotSet,
                        }
                    ],
                ),
            ]
        )
        fired_methods = instance._run_hooked_methods("after_create")
        self.assertEqual(fired_methods, ["method_that_does_fires"])

    def test_has_changed(self):
        data = self.stub_data
        data["username"] = "Joe"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(user_account.has_changed("username"))
        user_account.username = "Josephine"
        self.assertTrue(user_account.has_changed("username"))

    def test_has_changed_is_true_if_fk_related_model_field_has_changed(self):
        org = Organization.objects.create(name="Dunder Mifflin")
        UserAccount.objects.create(**self.stub_data, organization=org)
        user_account = UserAccount.objects.get()

        org.name = "Dwight's Paper Empire"
        org.save()
        user_account._clear_watched_fk_model_cache()
        self.assertTrue(user_account.has_changed("organization.name"))

    def test_has_changed_is_false_if_fk_related_model_field_has_not_changed(self):
        org = Organization.objects.create(name="Dunder Mifflin")
        UserAccount.objects.create(**self.stub_data, organization=org)
        user_account = UserAccount.objects.get()
        user_account._clear_watched_fk_model_cache()
        self.assertFalse(user_account.has_changed("organization.name"))

    def test_has_changed_specs(self):
        specs = {"when": "first_name", "has_changed": True}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()

        self.assertFalse(user_account._check_has_changed("first_name", specs))
        user_account.first_name = "Ned"
        self.assertTrue(user_account._check_has_changed("first_name", specs))

    def test_check_is_now_condition_wildcard_should_pass(self):
        specs = {"when": "first_name", "is_now": "*"}
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.first_name = "Ned"
        self.assertTrue(user_account._check_is_now_condition("first_name", specs))

    def test_check_is_now_condition_matching_value_should_pass(self):
        specs = {"when": "first_name", "is_now": "Ned"}
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.first_name = "Ned"
        self.assertTrue(user_account._check_is_now_condition("first_name", specs))

    def test_check_is_now_condition_not_matched_value_should_not_pass(self):
        specs = {"when": "first_name", "is_now": "Bart"}
        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(user_account._check_is_now_condition("first_name", specs))

    def test_check_was_not_condition_should_pass_when_not_set(self):
        specs = {"when": "first_name", "was_not": NotSet}
        data = self.stub_data
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(user_account._check_was_not_condition("first_name", specs))

    def test_check_was_not_condition_not_matching_value_should_pass(self):
        specs = {"when": "first_name", "was_not": "Bart"}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(user_account._check_was_not_condition("first_name", specs))

    def test_check_was_not_condition_matched_value_should_not_pass(self):
        specs = {"when": "first_name", "was_not": "Homer"}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(user_account._check_was_not_condition("first_name", specs))

    def test_check_was_condition_wildcard_should_pass(self):
        specs = {"when": "first_name", "was": "*"}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(user_account._check_was_condition("first_name", specs))

    def test_check_was_condition_matching_value_should_pass(self):
        specs = {"when": "first_name", "was": "Homer"}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(user_account._check_was_condition("first_name", specs))

    def test_check_was_condition_not_matched_value_should_not_pass(self):
        specs = {"when": "first_name", "was": "Bart"}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(user_account._check_was_condition("first_name", specs))

    def test_is_not_condition_should_pass(self):
        specs = {"when": "first_name", "is_not": "Ned"}

        data = self.stub_data
        data["first_name"] = "Homer"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertTrue(user_account._check_is_not_condition("first_name", specs))

    def test_is_not_condition_should_not_pass(self):
        specs = {"when": "first_name", "is_not": "Ned"}

        data = self.stub_data
        data["first_name"] = "Ned"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        self.assertFalse(user_account._check_is_not_condition("first_name", specs))

    def test_changes_to_condition_should_pass(self):
        data = self.stub_data
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        with self.assertRaises(CannotRename, msg="Oh, not Flanders. Anybody but Flanders."):
            user_account.last_name = "Flanders"
            user_account.save()

    def test_changes_to_condition_should_not_pass(self):
        data = self.stub_data
        data["first_name"] = "Marge"
        data["last_name"] = "Simpson"
        UserAccount.objects.create(**data)
        user_account = UserAccount.objects.get()
        user_account.last_name = "Bouvier"
        user_account.save()  # `CannotRename` exception is not raised

    def test_should_not_call_cached_property(self):
        """
            full_name is cached_property. Accessing _potentially_hooked_methods
            should not call it incidentally.
        """
        data = self.stub_data
        data["first_name"] = "Bart"
        data["last_name"] = "Simpson"
        account = UserAccount.objects.create(**data)
        account._potentially_hooked_methods
        account.first_name = "Bartholomew"
        # Should be first time this property is accessed...
        self.assertEqual(account.full_name, "Bartholomew Simpson")

    def test_comparison_state_should_reset_after_save(self):
        data = self.stub_data
        data["first_name"] = "Marge"
        data["last_name"] = "Simpson"
        account = UserAccount.objects.create(**data)
        account.first_name = "Maggie"
        self.assertTrue(account.has_changed("first_name"))
        account.save()
        self.assertFalse(account.has_changed("first_name"))
