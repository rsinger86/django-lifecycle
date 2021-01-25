from functools import reduce, lru_cache
from inspect import isfunction
from typing import Any, List

from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.utils.functional import cached_property

from . import NotSet
from .hooks import (
    BEFORE_CREATE,
    BEFORE_UPDATE,
    BEFORE_SAVE,
    BEFORE_DELETE,
    AFTER_CREATE,
    AFTER_UPDATE,
    AFTER_SAVE,
    AFTER_DELETE,
)

from .django_info import DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES


class LifecycleModelMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_state = self._snapshot_state()

    def _snapshot_state(self):
        state = self.__dict__.copy()

        for watched_related_field in self._watched_fk_model_fields():
            state[watched_related_field] = self._current_value(watched_related_field)

        if "_state" in state:
            del state["_state"]

        if "_potentially_hooked_methods" in state:
            del state["_potentially_hooked_methods"]

        if "_initial_state" in state:
            del state["_initial_state"]

        if "_watched_fk_model_fields" in state:
            del state["_watched_fk_model_fields"]

        return state

    @property
    def _diff_with_initial(self) -> dict:
        initial = self._initial_state
        current = self._snapshot_state()
        diffs = []

        for k, v in initial.items():
            if k in current and v != current[k]:
                diffs.append((k, (v, current[k])))

        return dict(diffs)

    def _sanitize_field_name(self, field_name: str) -> str:
        try:
            if self._meta.get_field(field_name).get_internal_type() == "ForeignKey":
                if not field_name.endswith("_id"):
                    return field_name + "_id"
        except FieldDoesNotExist:
            pass

        return field_name

    def _current_value(self, field_name: str) -> Any:
        if "." in field_name:

            def getitem(obj, field_name: str):
                try:
                    return getattr(obj, field_name)
                except (AttributeError, ObjectDoesNotExist):
                    return None

            return reduce(getitem, field_name.split("."), self)
        else:
            return getattr(self, self._sanitize_field_name(field_name))

    def initial_value(self, field_name: str) -> Any:
        """
        Get initial value of field when model was instantiated.
        """
        field_name = self._sanitize_field_name(field_name)

        if field_name in self._initial_state:
            return self._initial_state[field_name]

        return None

    def has_changed(self, field_name: str) -> bool:
        """
        Check if a field has changed since the model was instantiated.
        """
        changed = self._diff_with_initial.keys()
        field_name = self._sanitize_field_name(field_name)

        if field_name in changed:
            return True

        return False

    def _clear_watched_fk_model_cache(self):
        """

        """
        for watched_field_name in self._watched_fk_models():
            field = self._meta.get_field(watched_field_name)

            if field.is_relation and field.is_cached(self):
                field.delete_cached_value(self)

    def save(self, *args, **kwargs):
        skip_hooks = kwargs.pop("skip_hooks", False)
        save = super().save

        if skip_hooks:
            save(*args, **kwargs)
            return

        self._clear_watched_fk_model_cache()
        is_new = self._state.adding

        if is_new:
            self._run_hooked_methods(BEFORE_CREATE)
        else:
            self._run_hooked_methods(BEFORE_UPDATE)

        self._run_hooked_methods(BEFORE_SAVE)
        save(*args, **kwargs)
        self._run_hooked_methods(AFTER_SAVE)

        if is_new:
            self._run_hooked_methods(AFTER_CREATE)
        else:
            self._run_hooked_methods(AFTER_UPDATE)

        self._initial_state = self._snapshot_state()

    def delete(self, *args, **kwargs):
        self._run_hooked_methods(BEFORE_DELETE)
        value = super().delete(*args, **kwargs)
        self._run_hooked_methods(AFTER_DELETE)
        return value

    @classmethod
    @lru_cache(typed=True)
    def _potentially_hooked_methods(cls):
        skip = set(cls._get_unhookable_attribute_names())
        collected = []

        for name in dir(cls):
            if name in skip:
                continue
            try:
                attr = getattr(cls, name)
                if isfunction(attr) and hasattr(attr, "_hooked"):
                    collected.append(attr)
            except AttributeError:
                pass

        return collected

    @classmethod
    @lru_cache(typed=True)
    def _watched_fk_model_fields(cls) -> List[str]:
        """
            Gather up all field names (values in 'when' key) that correspond to
            field names on FK-related models. These will be strings that contain
            periods.
        """
        watched = []  # List[str]

        for method in cls._potentially_hooked_methods():
            for specs in method._hooked:
                if specs["when"] is not None and "." in specs["when"]:
                    watched.append(specs["when"])

        return watched

    @classmethod
    @lru_cache(typed=True)
    def _watched_fk_models(cls) -> List[str]:
        return [_.split(".")[0] for _ in cls._watched_fk_model_fields()]

    def _run_hooked_methods(self, hook: str) -> List[str]:
        """
            Iterate through decorated methods to find those that should be
            triggered by the current hook. If conditions exist, check them before
            running otherwise go ahead and run.
        """
        fired = []

        for method in self._potentially_hooked_methods():
            for callback_specs in method._hooked:
                if callback_specs["hook"] != hook:
                    continue

                when_field = callback_specs.get("when")
                when_any_field = callback_specs.get("when_any")

                if when_field:
                    if self._check_callback_conditions(when_field, callback_specs):
                        fired.append(method.__name__)
                        method(self)
                elif when_any_field:
                    for field_name in when_any_field:
                        if self._check_callback_conditions(field_name, callback_specs):
                            fired.append(method.__name__)
                            method(self)
                else:
                    fired.append(method.__name__)
                    method(self)

        return fired

    def _check_callback_conditions(self, field_name: str, specs: dict) -> bool:
        if not self._check_has_changed(field_name, specs):
            return False

        if not self._check_is_now_condition(field_name, specs):
            return False

        if not self._check_was_condition(field_name, specs):
            return False

        if not self._check_was_not_condition(field_name, specs):
            return False

        if not self._check_is_not_condition(field_name, specs):
            return False

        if not self._check_changes_to_condition(field_name, specs):
            return False

        return True

    def _check_has_changed(self, field_name: str, specs: dict) -> bool:
        has_changed = specs["has_changed"]
        return has_changed is None or has_changed == self.has_changed(field_name)

    def _check_is_now_condition(self, field_name: str, specs: dict) -> bool:
        return specs["is_now"] in (self._current_value(field_name), "*")

    def _check_is_not_condition(self, field_name: str, specs: dict) -> bool:
        is_not = specs["is_not"]
        return is_not is NotSet or self._current_value(field_name) != is_not

    def _check_was_condition(self, field_name: str, specs: dict) -> bool:
        return specs["was"] in (self.initial_value(field_name), "*")

    def _check_was_not_condition(self, field_name: str, specs: dict) -> bool:
        was_not = specs["was_not"]
        return was_not is NotSet or self.initial_value(field_name) != was_not

    def _check_changes_to_condition(self, field_name: str, specs: dict) -> bool:
        changes_to = specs["changes_to"]
        return any(
            [
                changes_to is NotSet,
                (
                    self.initial_value(field_name) != changes_to
                    and self._current_value(field_name) == changes_to
                ),
            ]
        )

    @classmethod
    def _get_model_property_names(cls) -> List[str]:
        """
            Gather up properties and cached_properties which may be methods
            that were decorated. Need to inspect class versions b/c doing
            getattr on them could cause unwanted side effects.
        """
        property_names = []

        for name in dir(cls):
            attr = getattr(cls, name, None)

            if attr and (
                isinstance(attr, property) or isinstance(attr, cached_property)
            ):
                property_names.append(name)

        return property_names

    @classmethod
    def _get_model_descriptor_names(cls) -> List[str]:
        """
        Attributes which are Django descriptors. These represent a field
        which is a one-to-many or many-to-many relationship that is
        potentially defined in another model, and doesn't otherwise appear
        as a field on this model.
        """

        descriptor_names = []

        for name in dir(cls):
            attr = getattr(cls, name, None)

            if attr and isinstance(attr, DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES):
                descriptor_names.append(name)

        return descriptor_names

    @classmethod
    def _get_field_names(cls) -> List[str]:
        names = []

        for f in cls._meta.get_fields():
            names.append(f.name)

            try:
                internal_type = cls._meta.get_field(f.name).get_internal_type()
            except AttributeError:
                # Skip fields which don't provide a `get_internal_type` method, e.g. GenericForeignKey
                continue
            else:
                if internal_type == "ForeignKey":
                    names.append(f.name + "_id")

        return names

    @classmethod
    def _get_unhookable_attribute_names(cls) -> List[str]:
        return (
            cls._get_field_names()
            + cls._get_model_descriptor_names()
            + cls._get_model_property_names()
            + ["_run_hooked_methods"]
        )
