from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Iterable
from typing import Union

from ..constants import NotSet
from ..conditions.base import ChainableCondition


__all__ = [
    "WhenFieldValueWas",
    "WhenFieldValueIs",
    "WhenFieldHasChanged",
    "WhenFieldValueIsNot",
    "WhenFieldValueWasNot",
    "WhenFieldValueChangesTo",
    "Always",
]


@dataclass
class WhenFieldValueWas(ChainableCondition):
    field_name: str
    value: Any = "*"

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        return self.value in (instance.initial_value(self.field_name), "*")


@dataclass
class WhenFieldValueIs(ChainableCondition):
    field_name: str
    value: Any = "*"

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        return self.value in (instance._current_value(self.field_name), "*")


@dataclass
class WhenFieldHasChanged(ChainableCondition):
    field_name: str
    has_changed: bool | None = None

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        is_partial_fields_update = update_fields is not None
        is_synced = is_partial_fields_update is False or self.field_name in update_fields
        if not is_synced:
            return False

        return self.has_changed is None or self.has_changed == instance.has_changed(self.field_name)


@dataclass
class WhenFieldValueIsNot(ChainableCondition):
    field_name: str
    value: Any = NotSet

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        return self.value is NotSet or instance._current_value(self.field_name) != self.value


@dataclass
class WhenFieldValueWasNot(ChainableCondition):
    field_name: str
    value: Any = NotSet

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        return self.value is NotSet or instance.initial_value(self.field_name) != self.value


@dataclass
class WhenFieldValueChangesTo(ChainableCondition):
    field_name: str
    value: Any = NotSet

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        is_partial_fields_update = update_fields is not None
        is_synced = is_partial_fields_update is False or self.field_name in update_fields
        if not is_synced:
            return False

        value_has_changed = bool(instance.initial_value(self.field_name) != self.value)
        new_value_is_the_expected = bool(instance._current_value(self.field_name) == self.value)
        return self.value is NotSet or (value_has_changed and new_value_is_the_expected)


class Always:
    def __call__(self, instance: Any, update_fields=None):
        return True
