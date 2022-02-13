from functools import wraps
from typing import List, Optional

from django_lifecycle import NotSet

from .hooks import VALID_HOOKS


class DjangoLifeCycleException(Exception):
    pass


def _validate_hook_params(hook, when, when_any, has_changed, on_commit):
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
    
    if on_commit is not None:
        if not hook.startswith("after_"):
            raise DjangoLifeCycleException("'on_commit' hook param is only valid with AFTER_* hooks")

        if not isinstance(on_commit, bool):
            raise DjangoLifeCycleException("'on_commit' hook param must be a boolean")


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
    on_commit: Optional[bool] = None
):
    _validate_hook_params(hook, when, when_any, has_changed, on_commit)

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
                "on_commit": on_commit
            }
        )

        return func

    return decorator
