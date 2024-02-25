from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional

from django_lifecycle import NotSet
from django_lifecycle.conditions.base import ChainableCondition
from django_lifecycle.conditions import WhenFieldChangesTo
from django_lifecycle.conditions import WhenFieldHasChanged
from django_lifecycle.conditions import WhenFieldIsNot
from django_lifecycle.conditions import WhenFieldIsNow
from django_lifecycle.conditions import WhenFieldWas
from django_lifecycle.conditions import WhenFieldWasNot


@dataclass
class When(ChainableCondition):
    when: Optional[str] = None
    was: Any = "*"
    is_now: Any = "*"
    has_changed: Optional[bool] = None
    is_not: Any = NotSet
    was_not: Any = NotSet
    changes_to: Any = NotSet

    def __call__(self, instance: Any, update_fields=None) -> bool:
        has_changed_condition = WhenFieldHasChanged(
            self.when, has_changed=self.has_changed
        )
        if not has_changed_condition(instance, update_fields=update_fields):
            return False

        changes_to_condition = WhenFieldChangesTo(self.when, changes_to=self.changes_to)
        if not changes_to_condition(instance, self.when):
            return False

        is_now_condition = WhenFieldIsNow(self.when, is_now=self.is_now)
        if not is_now_condition(instance, self.when):
            return False

        was_condition = WhenFieldWas(self.when, was=self.was)
        if not was_condition(instance, self.when):
            return False

        was_not_condition = WhenFieldWasNot(self.when, was_not=self.was_not)
        if not was_not_condition(instance, self.when):
            return False

        is_not_condition = WhenFieldIsNot(self.when, is_not=self.is_not)
        if not is_not_condition(instance, self.when):
            return False

        return True


@dataclass
class WhenAny:
    when_any: Optional[List[str]] = None
    was: Any = "*"
    is_now: Any = "*"
    has_changed: Optional[bool] = None
    is_not: Any = NotSet
    was_not: Any = NotSet
    changes_to: Any = NotSet

    def __call__(self, instance: Any, update_fields=None) -> bool:
        conditions = (
            When(
                when=field,
                was=self.was,
                is_now=self.is_now,
                has_changed=self.has_changed,
                is_not=self.is_not,
                was_not=self.was_not,
                changes_to=self.changes_to,
            )
            for field in self.when_any
        )
        return any(
            condition(instance, update_fields=update_fields) for condition in conditions
        )
