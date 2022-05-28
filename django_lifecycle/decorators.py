from dataclasses import dataclass
from functools import wraps
from typing import Any
from typing import List, Optional

from django_lifecycle import NotSet
from .dataclass_validation import Validations
from .hooks import VALID_HOOKS
from .priority import DEFAULT_PRIORITY


class DjangoLifeCycleException(Exception):
    pass


@dataclass(order=False)
class HookConfig(Validations):
    hook: str
    when: Optional[str] = None
    when_any: Optional[List[str]] = None
    was: Any = "*"
    is_now: Any = "*"
    has_changed: Optional[bool] = None
    is_not: Any = NotSet
    was_not: Any = NotSet
    changes_to: Any = NotSet
    on_commit: bool = False
    priority: int = DEFAULT_PRIORITY

    def validate_hook(self, value, **kwargs):
        if value not in VALID_HOOKS:
            raise DjangoLifeCycleException(
                "%s is not a valid hook; must be one of %s" % (hook, VALID_HOOKS)
            )

        return value

    def validate_when(self, value, **kwargs):
        if value is not None and not isinstance(value, str):
            raise DjangoLifeCycleException(
                "'when' hook param must be a string matching the name of a model field"
            )

        return value

    def validate_when_any(self, value, **kwargs):
        if value is None:
            return

        when_any_error_msg = (
            "'when_any' hook param must be a list of strings "
            "matching the names of model fields"
        )

        if not isinstance(value, list):
            raise DjangoLifeCycleException(when_any_error_msg)

        if len(value) == 0:
            raise DjangoLifeCycleException(
                "'when_any' hook param must contain at least one field name"
            )

        for field_name in value:
            if not isinstance(field_name, str):
                raise DjangoLifeCycleException(when_any_error_msg)

        return value

    def validate_has_changed(self, value, **kwargs):
        if value is not None and not isinstance(value, bool):
            raise DjangoLifeCycleException("'has_changed' hook param must be a boolean")

        return value

    def validate_on_commit(self, value, **kwargs):
        if value is None:
            return

        if not isinstance(value, bool):
            raise DjangoLifeCycleException("'on_commit' hook param must be a boolean")

        return value

    def validate_priority(self, value, **kwargs):
        if self.priority < 0:
            raise DjangoLifeCycleException(
                "'priority' hook param must be a positive integer"
            )

        return value

    def validate_on_commit_only_for_after_hooks(self):
        if self.on_commit and not self.hook.startswith("after_"):
            raise DjangoLifeCycleException(
                "'on_commit' hook param is only valid with AFTER_* hooks"
            )

    def validate_when_and_when_any(self):
        if self.when is not None and self.when_any is not None:
            raise DjangoLifeCycleException(
                "Can pass either 'when' or 'when_any' but not both"
            )

    def validate(self):
        self.validate_when_and_when_any()
        self.validate_on_commit_only_for_after_hooks()

    def __lt__(self, other):
        if not isinstance(other, HookConfig):
            return NotImplemented

        return self.priority < other.priority

    def __call__(self, hooked_method):
        if not hasattr(hooked_method, "_hooked"):

            @wraps(hooked_method)
            def func(*args, **kwargs):
                hooked_method(*args, **kwargs)

            func._hooked = []
        else:
            func = hooked_method

        func._hooked.append(self)

        # Sort hooked methods by priority
        func._hooked = sorted(func._hooked)

        return func


hook = HookConfig  # keep backwards compatibility
