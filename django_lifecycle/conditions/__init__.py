from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Iterable
from typing import Union

from django_lifecycle import NotSet
from django_lifecycle.conditions.base import ChainableCondition


__all__ = [
    "WhenFieldWas",
    "WhenFieldIsNow",
    "WhenFieldHasChanged",
    "WhenFieldIsNot",
    "WhenFieldWasNot",
    "WhenFieldChangesTo",
    "Always",
]


@dataclass
class WhenFieldWas(ChainableCondition):
    field_name: str
    was: Any = "*"

    def __call__(
        self, instance: Any, update_fields: Union[Iterable[str], None] = None
    ) -> bool:
        return self.was in (instance.initial_value(self.field_name), "*")


@dataclass
class WhenFieldIsNow(ChainableCondition):
    field_name: str
    is_now: Any = "*"

    def __call__(
        self, instance: Any, update_fields: Union[Iterable[str], None] = None
    ) -> bool:
        return self.is_now in (instance._current_value(self.field_name), "*")


@dataclass
class WhenFieldHasChanged(ChainableCondition):
    field_name: str
    has_changed: bool | None = None

    def __call__(
        self, instance: Any, update_fields: Union[Iterable[str], None] = None
    ) -> bool:
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
class WhenFieldIsNot(ChainableCondition):
    field_name: str
    is_not: Any = NotSet

    def __call__(
        self, instance: Any, update_fields: Union[Iterable[str], None] = None
    ) -> bool:
        return (
            self.is_not is NotSet
            or instance._current_value(self.field_name) != self.is_not
        )


@dataclass
class WhenFieldWasNot(ChainableCondition):
    field_name: str
    was_not: Any = NotSet

    def __call__(
        self, instance: Any, update_fields: Union[Iterable[str], None] = None
    ) -> bool:
        return (
            self.was_not is NotSet
            or instance.initial_value(self.field_name) != self.was_not
        )


@dataclass
class WhenFieldChangesTo(ChainableCondition):
    field_name: str
    changes_to: Any = NotSet

    def __call__(
        self, instance: Any, update_fields: Union[Iterable[str], None] = None
    ) -> bool:
        is_partial_fields_update = update_fields is not None
        is_synced = (
            is_partial_fields_update is False or self.field_name in update_fields
        )
        if not is_synced:
            return False

        value_has_changed = bool(
            instance.initial_value(self.field_name) != self.changes_to
        )
        new_value_is_the_expected = bool(
            instance._current_value(self.field_name) == self.changes_to
        )
        return self.changes_to is NotSet or (
            value_has_changed and new_value_is_the_expected
        )


class Always:
    def __call__(self, instance: Any, update_fields=None):
        return True
