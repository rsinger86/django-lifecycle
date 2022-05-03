from dataclasses import dataclass, field
from functools import wraps
from typing import List, Optional, Any

from django_lifecycle import NotSet

from .hooks import VALID_HOOKS


class DjangoLifeCycleException(Exception):
    pass


@dataclass
class HookConfig:
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

    def __post_init__(self):
        if self.hook not in VALID_HOOKS:
            raise DjangoLifeCycleException(
                "%s is not a valid hook; must be one of %s" % (hook, VALID_HOOKS)
            )

        if self.has_changed is not None and not isinstance(self.has_changed, bool):
            raise DjangoLifeCycleException("'has_changed' hook param must be a boolean")

        if self.when is not None and not isinstance(self.when, str):
            raise DjangoLifeCycleException(
                "'when' hook param must be a string matching the name of a model field"
            )

        if self.when_any is not None:
            when_any_error_msg = (
                "'when_any' hook param must be a list of strings "
                "matching the names of model fields"
            )

            if not isinstance(self.when_any, list):
                raise DjangoLifeCycleException(when_any_error_msg)

            if len(self.when_any) == 0:
                raise DjangoLifeCycleException(
                    "'when_any' hook param must contain at least one field name"
                )

            for field_name in self.when_any:
                if not isinstance(field_name, str):
                    raise DjangoLifeCycleException(when_any_error_msg)

        if self.when is not None and self.when_any is not None:
            raise DjangoLifeCycleException(
                "Can pass either 'when' or 'when_any' but not both"
            )

        if self.on_commit:
            if not self.hook.startswith("after_"):
                raise DjangoLifeCycleException(
                    "'on_commit' hook param is only valid with AFTER_* hooks"
                )

            if not isinstance(self.on_commit, bool):
                raise DjangoLifeCycleException(
                    "'on_commit' hook param must be a boolean"
                )

    def __call__(self, hooked_method):
        if not hasattr(hooked_method, "_hooked"):

            @wraps(hooked_method)
            def func(*args, **kwargs):
                hooked_method(*args, **kwargs)

            func._hooked = []
        else:
            func = hooked_method

        func._hooked.append(self)

        return func


hook = HookConfig  # keep backwards compatibility
