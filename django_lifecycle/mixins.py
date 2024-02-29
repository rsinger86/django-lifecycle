from __future__ import annotations
from copy import deepcopy
from functools import partial, reduce, lru_cache
from inspect import isfunction
from typing import Any, List
from typing import Iterable

from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import transaction
from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor,
    ReverseOneToOneDescriptor,
    ReverseManyToOneDescriptor,
    ManyToManyDescriptor,
    ForwardOneToOneDescriptor,
)
from django.utils.functional import cached_property

from .abstract import AbstractHookedMethod
from .decorators import HookConfig
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


DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES = (
    ForwardManyToOneDescriptor,
    ForwardOneToOneDescriptor,
    ManyToManyDescriptor,
    ReverseManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)


class HookedMethod(AbstractHookedMethod):
    @property
    def name(self) -> str:
        return self.method.__name__

    def run(self, instance: Any) -> None:
        self.method(instance)


class OnCommitHookedMethod(AbstractHookedMethod):
    """Hooked method that should run on_commit"""

    @property
    def name(self) -> str:
        # Append `_on_commit` to the existing method name to allow for firing
        # the same hook within the atomic transaction and on_commit
        return f"{self.method.__name__}_on_commit"

    def run(self, instance: Any) -> None:
        # Use partial to create a function closure that binds `self`
        # to ensure it's available to execute later.
        _on_commit_func = partial(self.method, instance)
        _on_commit_func.__name__ = self.name
        transaction.on_commit(_on_commit_func)


def instantiate_hooked_method(
    method: Any, callback_specs: HookConfig
) -> AbstractHookedMethod:
    hooked_method_class = (
        OnCommitHookedMethod if callback_specs.on_commit else HookedMethod
    )
    return hooked_method_class(
        method=method,
        priority=callback_specs.priority,
    )


class LifecycleModelMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_state = self._snapshot_state()

    def _snapshot_state(self):
        state = deepcopy(self.__dict__)

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
            field = self._meta.get_field(field_name)

            try:
                internal_type = field.get_internal_type()
            except AttributeError:
                return field
            if internal_type == "ForeignKey" or internal_type == "OneToOneField":
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
        Get initial value of field when model value instantiated.
        """
        field_name = self._sanitize_field_name(field_name)

        if field_name in self._initial_state:
            return self._initial_state[field_name]

        return None

    def has_changed(self, field_name: str) -> bool:
        """
        Check if a field has changed since the model value instantiated.
        """
        changed = self._diff_with_initial.keys()
        field_name = self._sanitize_field_name(field_name)

        if field_name in changed:
            return True

        return False

    def _clear_watched_fk_model_cache(self):
        """ """
        for watched_field_name in self._watched_fk_models():
            field = self._meta.get_field(watched_field_name)

            if field.is_relation and field.is_cached(self):
                field.delete_cached_value(self)

    def _reset_initial_state(self):
        self._initial_state = self._snapshot_state()

    @transaction.atomic
    def save(self, *args, **kwargs):
        skip_hooks = kwargs.pop("skip_hooks", False)
        save = super().save

        if skip_hooks:
            save(*args, **kwargs)
            return

        self._clear_watched_fk_model_cache()
        is_new = self._state.adding

        if is_new:
            self._run_hooked_methods(BEFORE_CREATE, **kwargs)
        else:
            self._run_hooked_methods(BEFORE_UPDATE, **kwargs)

        self._run_hooked_methods(BEFORE_SAVE, **kwargs)
        save(*args, **kwargs)
        self._run_hooked_methods(AFTER_SAVE, **kwargs)

        if is_new:
            self._run_hooked_methods(AFTER_CREATE, **kwargs)
        else:
            self._run_hooked_methods(AFTER_UPDATE, **kwargs)

        transaction.on_commit(self._reset_initial_state)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self._run_hooked_methods(BEFORE_DELETE, **kwargs)
        value = super().delete(*args, **kwargs)
        self._run_hooked_methods(AFTER_DELETE, **kwargs)
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
            for hook_config in method._hooked:
                if hook_config.when is not None and "." in hook_config.when:
                    watched.append(hook_config.when)

        return watched

    @classmethod
    @lru_cache(typed=True)
    def _watched_fk_models(cls) -> List[str]:
        return [_.split(".")[0] for _ in cls._watched_fk_model_fields()]

    def _get_hooked_methods(
        self, hook: str, update_fields: Iterable[str] | None = None, **kwargs
    ) -> List[AbstractHookedMethod]:
        """
        Iterate through decorated methods to find those that should be
        triggered by the current hook. If conditions exist, check them before
        adding it to the list of methods to fire.

        Then, sort the list.
        """

        hooked_methods = []

        for method in self._potentially_hooked_methods():
            for callback_specs in method._hooked:
                if callback_specs.hook != hook:
                    continue

                if callback_specs.condition(self, update_fields=update_fields):
                    hooked_method = instantiate_hooked_method(method, callback_specs)
                    hooked_methods.append(hooked_method)

                    # Only store the method once per hook
                    break

        return sorted(hooked_methods)

    def _run_hooked_methods(self, hook: str, **kwargs) -> List[str]:
        """Run hooked methods"""
        fired = []

        for method in self._get_hooked_methods(hook, **kwargs):
            method.run(self)
            fired.append(method.name)

        return fired

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

            field = cls._meta.get_field(f.name)
            try:
                internal_type = field.get_internal_type()
            except AttributeError:
                continue

            if internal_type == "ForeignKey" or internal_type == "OneToOneField":
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
