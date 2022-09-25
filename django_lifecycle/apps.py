from django.apps import AppConfig
from django.core.checks import register, Tags


class DjangoLifecycleConfig(AppConfig):
    name = "django_lifecycle"

    def ready(self) -> None:
        super().ready()

        from .checks.inherits_lifecycle_model_mixin import (
            check_models_with_hooked_methods_inherit_from_lifecycle,
        )

        register(check_models_with_hooked_methods_inherit_from_lifecycle, Tags.models)
