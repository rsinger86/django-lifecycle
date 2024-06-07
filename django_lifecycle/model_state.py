from __future__ import annotations
from typing import Any
from typing import Dict
from typing import TYPE_CHECKING

from django_lifecycle.utils import get_value
from django_lifecycle.utils import sanitize_field_name

if TYPE_CHECKING:
    from django_lifecycle import LifecycleModelMixin


class ModelState:
    def __init__(self, initial_state: Dict[str, Any]):
        self.initial_state = initial_state

    @classmethod
    def from_instance(cls, instance: "LifecycleModelMixin") -> ModelState:
        state = instance.__dict__.copy()

        for watched_related_field in instance._watched_fk_model_fields():
            state[watched_related_field] = get_value(instance, watched_related_field)

        fields_to_remove = (
            "_state",
            "_potentially_hooked_methods",
            "_initial_state",
            "_watched_fk_model_fields",
        )
        for field in fields_to_remove:
            state.pop(field, None)

        return ModelState(state)

    def get_diff(self, instance: "LifecycleModelMixin") -> dict:
        current = ModelState.from_instance(instance).initial_state
        diffs = {}

        for key, initial_value in self.initial_state.items():
            try:
                current_value = current[key]
            except KeyError:
                continue

            if initial_value != current_value:
                diffs[key] = (key, current_value)

        return diffs

    def get_value(self, instance: "LifecycleModelMixin", field_name: str) -> Any:
        """
        Get initial value of field when model was instantiated.
        """
        field_name = sanitize_field_name(instance, field_name)
        return self.initial_state.get(field_name)

    def has_changed(self, instance: "LifecycleModelMixin", field_name: str) -> bool:
        """
        Check if a field has changed since the model was instantiated.
        """
        field_name = sanitize_field_name(instance, field_name)
        return field_name in self.get_diff(instance)
