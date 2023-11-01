import inspect
from typing import Iterable
from typing import Type
from typing import Union

from django.apps import AppConfig
from django.apps import apps
from django.core.checks import Error
from django.core.checks import Tags
from django.core.checks import register
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


def model_has_lifecycle_mixin(model: Type[models.Model]) -> bool:
    from django_lifecycle.mixins import LifecycleModelMixin

    return issubclass(model, LifecycleModelMixin)


def check_models_with_hooked_methods_inherit_from_lifecycle(
    app_configs: Union[Iterable[AppConfig], None] = None, **kwargs
):
    for model in get_models_to_check(app_configs):
        if model_has_hooked_methods(model) and not model_has_lifecycle_mixin(model):
            yield Error(
                "Model has hooked methods but it doesn't inherit from LifecycleModelMixin",
                id="django_lifecycle.E001",
                obj=model,
            )


class ChecksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_lifecycle_checks"

    def ready(self) -> None:
        super().ready()

        register(check_models_with_hooked_methods_inherit_from_lifecycle, Tags.models)
