from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional

from ..constants import NotSet
from ..conditions.base import ChainableCondition
from ..conditions import WhenFieldValueChangesTo
from ..conditions import WhenFieldHasChanged
from ..conditions import WhenFieldValueIsNot
from ..conditions import WhenFieldValueIs
from ..conditions import WhenFieldValueWas
from ..conditions import WhenFieldValueWasNot


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
        has_changed_condition = WhenFieldHasChanged(self.when, has_changed=self.has_changed)
        if not has_changed_condition(instance, update_fields=update_fields):
            return False

        changes_to_condition = WhenFieldValueChangesTo(self.when, value=self.changes_to)
        if not changes_to_condition(instance, self.when):
            return False

        is_now_condition = WhenFieldValueIs(self.when, value=self.is_now)
        if not is_now_condition(instance, self.when):
            return False

        was_condition = WhenFieldValueWas(self.when, value=self.was)
        if not was_condition(instance, self.when):
            return False

        was_not_condition = WhenFieldValueWasNot(self.when, value=self.was_not)
        if not was_not_condition(instance, self.when):
            return False

        is_not_condition = WhenFieldValueIsNot(self.when, value=self.is_not)
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
        return any(condition(instance, update_fields=update_fields) for condition in conditions)
