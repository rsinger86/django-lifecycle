import inspect
from typing import Iterable, Type, Union

from django.apps import AppConfig, apps
from django.core.checks import Error, register, Tags
from django.db import models


def get_models_to_check(
    app_configs: Union[Iterable[AppConfig], None]
) -> Iterable[Type[models.Model]]:
    app_configs = app_configs or apps.get_app_configs()
    for app_config in app_configs:
        yield from app_config.get_models()


def model_has_hooked_methods(model: Type[models.Model]) -> bool:
    for attribute_name, attribute in inspect.getmembers(
        model, predicate=inspect.isfunction
    ):
        if hasattr(attribute, "_hooked"):
            return True
    return False


def check_models_with_hooked_methods_inherit_from_lifecycle(
    app_configs: Union[Iterable[AppConfig], None] = None, **kwargs
):
    from django_lifecycle import LifecycleModelMixin

    for model in get_models_to_check(app_configs):
        if model_has_hooked_methods(model) and not issubclass(
            model, LifecycleModelMixin
        ):
            yield Error(
                "Model has hooked methods but it doesn't inherit from LifecycleModelMixin",
                id="django_lifecycle.E001",
                obj=model,
            )
