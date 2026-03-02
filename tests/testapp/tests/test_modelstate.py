from django.test import TestCase
from datetime import datetime, UTC

from django_lifecycle.model_state import ModelState
from tests.testapp.models import UserAccount, Organization


class ModelStateTests(TestCase):
    def test_get_diff(self):
        simpsons = Organization(id=1, name="The Simpsons")
        homer = UserAccount(
            username="homer",
            first_name="Homer",
            last_name="Simpson",
            password="donuts",
            email="homer@simpsons.net",
            password_updated_at=None,
            joined_at=datetime(1987, 4, 19, 19, tzinfo=UTC),
            has_trial=False,
            organization=simpsons,
            name_changes=0,
            configurations={"foo": 1},
            status="active",
        )
        flanders = Organization(id=2, name="Flanders")
        ned = UserAccount(
            username="ned",
            first_name="Nedward",
            last_name="Flanders",
            password="jesus",
            email="ned@flanders.org",
            password_updated_at=datetime(2026, 3, 1, tzinfo=UTC),
            joined_at=datetime(1987, 4, 19, 20, tzinfo=UTC),
            has_trial=True,
            organization=flanders,
            name_changes=1,
            configurations={"bar": 1},
            status="inactive",
        )

        diff = ModelState.from_instance(homer).get_diff(ned)
        self.assertEqual(
            diff,
            {
                "username": ("homer", "ned"),
                "first_name": ("Homer", "Nedward"),
                "last_name": ("Simpson", "Flanders"),
                "password": ("donuts", "jesus"),
                "email": ("homer@simpsons.net", "ned@flanders.org"),
                "password_updated_at": (None, datetime(2026, 3, 1, tzinfo=UTC)),
                "joined_at": (
                    datetime(1987, 4, 19, 19, 0, tzinfo=UTC),
                    datetime(1987, 4, 19, 20, 0, tzinfo=UTC),
                ),
                "has_trial": (False, True),
                "organization_id": (1, 2),
                "organization.name": ("The Simpsons", "Flanders"),
                "name_changes": (0, 1),
                "configurations": ({"foo": 1}, {"bar": 1}),
                "status": ("active", "inactive"),
            },
        )
