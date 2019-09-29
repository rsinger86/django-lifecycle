from distutils.version import StrictVersion
from functools import reduce
from inspect import ismethod
from typing import Any, List

import django
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property

from .django_info import BACKWARDS_COMPATIBILITY
from .utils import get_unhookable_attribute_names


class NotSet(object):
    pass


def hook(
    hook: str,
    when: str = None,
    was="*",
    is_now="*",
    has_changed: bool = None,
    is_not=NotSet,
    was_not=NotSet,
):
    assert hook in (
        "before_save",
        "after_save",
        "before_create",
        "after_create",
        "before_update",
        "after_update",
        "before_delete",
        "after_delete",
    )

    def decorator(hooked_method):
        if not hasattr(hooked_method, "_hooked"):

            def func(*args, **kwargs):
                hooked_method(*args, **kwargs)

            func._hooked = []
        else:
            func = hooked_method

        func._hooked.append(
            {
                "hook": hook,
                "when": when,
                "was": was,
                "is_now": is_now,
                "has_changed": has_changed,
                "is_not": is_not,
                "was_not": was_not,
            }
        )

        return func

    return decorator


class LifecycleModelMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_state = self._snapshot_state()

    def _snapshot_state(self):
        state = self.__dict__.copy()

        for watched_related_field in self._watched_fk_model_fields:
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
        for watched_field_name in self._watched_fk_models:
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
            self._run_hooked_methods("before_create")
        else:
            self._run_hooked_methods("before_update")

        self._run_hooked_methods("before_save")
        save(*args, **kwargs)
        self._run_hooked_methods("after_save")

        if is_new:
            self._run_hooked_methods("after_create")
        else:
            self._run_hooked_methods("after_update")

        self._initial_state = self._snapshot_state()

    def delete(self, *args, **kwargs):
        self._run_hooked_methods("before_delete")
        super().delete(*args, **kwargs)
        self._run_hooked_methods("after_delete")

    @cached_property
    def _potentially_hooked_methods(self):
        skip = set(get_unhookable_attribute_names(self))
        collected = []

        for name in dir(self):
            if name in skip:
                continue
            try:
                attr = getattr(self, name)
                if ismethod(attr) and hasattr(attr, "_hooked"):
                    collected.append(attr)
            except AttributeError:
                pass

        return collected

    @cached_property
    def _watched_fk_model_fields(self) -> List[str]:
        """
            Gather up all field names (values in 'when' key) that correspond to
            field names on FK-related models. These will be strings that contain
            periods.
        """
        watched: List[str] = []

        for method in self._potentially_hooked_methods:
            for specs in method._hooked:
                if specs["when"] is not None and "." in specs["when"]:
                    watched.append(specs["when"])

        return watched

    @cached_property
    def _watched_fk_models(self) -> List[str]:
        return [_.split(".")[0] for _ in self._watched_fk_model_fields]

    def _run_hooked_methods(self, hook: str):
        """
            Iterate through decorated methods to find those that should be
            triggered by the current hook. If conditions exist, check them before
            running otherwise go ahead and run.
        """
        for method in self._potentially_hooked_methods:
            for callback_specs in method._hooked:
                if callback_specs["hook"] != hook:
                    continue

                when = callback_specs.get("when")

                if when:
                    if self._check_callback_conditions(callback_specs):
                        method()
                else:
                    method()

    def _check_callback_conditions(self, specs: dict) -> bool:
        if not self._check_has_changed(specs):
            return False

        if not self._check_is_now_condition(specs):
            return False

        if not self._check_was_condition(specs):
            return False

        if not self._check_was_not_condition(specs):
            return False

        if not self._check_is_not_condition(specs):
            return False

        return True

    def _check_has_changed(self, specs: dict) -> bool:
        field_name = specs["when"]
        has_changed = specs["has_changed"]

        if has_changed is None:
            return True

        return has_changed == self.has_changed(field_name)

    def _check_is_now_condition(self, specs: dict) -> bool:
        field_name = specs["when"]
        return specs["is_now"] in (self._current_value(field_name), "*")

    def _check_is_not_condition(self, specs: dict) -> bool:
        field_name = specs["when"]
        is_not = specs["is_not"]
        return is_not is NotSet or self._current_value(field_name) != is_not

    def _check_was_condition(self, specs: dict) -> bool:
        field_name = specs["when"]
        return specs["was"] in (self.initial_value(field_name), "*")

    def _check_was_not_condition(self, specs: dict) -> bool:
        field_name = specs["when"]
        was_not = specs["was_not"]
        return was_not is NotSet or self.initial_value(field_name) != was_not


# For backwards compatibility and Django 1.8
if BACKWARDS_COMPATIBILITY:

    class LifecycleModel(LifecycleModelMixin, models.Model):
        class Meta:
            abstract = True
