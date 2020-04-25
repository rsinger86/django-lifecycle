from functools import wraps
from typing import List

from django_lifecycle import NotSet

from .hooks import VALID_HOOKS


class DjangoLifeCycleException(Exception):
    pass


def _validate_hook_params(hook, when, when_any, has_changed):
    if hook not in VALID_HOOKS:
        raise DjangoLifeCycleException(
            "%s is not a valid hook; must be one of %s" % (hook, VALID_HOOKS)
        )

    if has_changed is not None and not isinstance(has_changed, bool):
        raise DjangoLifeCycleException("'has_changed' hook param must be a boolean")

    if when is not None and not isinstance(when, str):
        raise DjangoLifeCycleException(
            "'when' hook param must be a string matching the name of a model field"
        )

    if when_any is not None:
        when_any_error_msg = (
            "'when_any' hook param must be a list of strings "
            "matching the names of model fields"
        )

        if not isinstance(when_any, list):
            raise DjangoLifeCycleException(when_any_error_msg)

        if len(when_any) == 0:
            raise DjangoLifeCycleException(
                "'when_any' hook param must contain at least one field name"
            )

        for field_name in when_any:
            if not isinstance(field_name, str):
                raise DjangoLifeCycleException(when_any_error_msg)

    if when is not None and when_any is not None:
        raise DjangoLifeCycleException(
            "Can pass either 'when' or 'when_any' but not both"
        )


def hook(
    hook: str,
    when: str = None,
    when_any: List[str] = None,
    was="*",
    is_now="*",
    has_changed: bool = None,
    is_not=NotSet,
    was_not=NotSet,
    changes_to=NotSet,
):
    _validate_hook_params(hook, when, when_any, has_changed)

    def decorator(hooked_method):
        if not hasattr(hooked_method, "_hooked"):

            @wraps(hooked_method)
            def func(*args, **kwargs):
                hooked_method(*args, **kwargs)

            func._hooked = []
        else:
            func = hooked_method

        func._hooked.append(
            {
                "hook": hook,
                "when": when,
                "when_any": when_any,
                "has_changed": has_changed,
                "is_now": is_now,
                "is_not": is_not,
                "was": was,
                "was_not": was_not,
                "changes_to": changes_to,
            }
        )

        return func

    return decorator
