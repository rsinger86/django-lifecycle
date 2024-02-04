from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Optional


from django_lifecycle import NotSet


@dataclass
class WhenFieldWas:
    field_name: str
    was: Any = "*"

    def __call__(self, instance: Any, update_fields=None) -> bool:
        return self.was in (instance.initial_value(self.field_name), "*")


@dataclass
class WhenFieldIsNow:
    field_name: str
    is_now: Any = "*"

    def __call__(self, instance: Any, update_fields=None) -> bool:
        return self.is_now in (instance._current_value(self.field_name), "*")


@dataclass
class WhenFieldHasChanged:
    field_name: str
    has_changed: bool | None = None

    def __call__(self, instance: Any, update_fields=None) -> bool:
        is_partial_fields_update = update_fields is not None
        is_synced = (
            is_partial_fields_update is False or self.field_name in update_fields
        )
        if not is_synced:
            return False

        return self.has_changed is None or self.has_changed == instance.has_changed(
            self.field_name
        )


@dataclass
class WhenFieldIsNot:
    field_name: str
    is_not: Any = NotSet

    def __call__(self, instance: Any, update_fields=None) -> bool:
        return (
            self.is_not is NotSet
            or instance._current_value(self.field_name) != self.is_not
        )


@dataclass
class WhenFieldWasNot:
    field_name: str
    was_not: Any = NotSet

    def __call__(self, instance: Any, update_fields=None) -> bool:
        return (
            self.was_not is NotSet
            or instance.initial_value(self.field_name) != self.was_not
        )


@dataclass
class WhenFieldChangesTo:
    field_name: str
    changes_to: Any = NotSet

    def __call__(self, instance: Any, update_fields=None) -> bool:
        is_partial_fields_update = update_fields is not None
        is_synced = (
            is_partial_fields_update is False or self.field_name in update_fields
        )
        if not is_synced:
            return False

        return any(
            [
                self.changes_to is NotSet,
                (
                    instance.initial_value(self.field_name) != self.changes_to
                    and instance._current_value(self.field_name) == self.changes_to
                ),
            ]
        )


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
            WhenCondition(
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


@dataclass
class WhenCondition:
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
