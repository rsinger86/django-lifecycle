from functools import reduce
from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


def sanitize_field_name(instance: models.Model, field_name: str) -> str:
    try:
        field = instance._meta.get_field(field_name)

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


def get_value(instance, sanitized_field_name: str) -> Any:
    if "." in sanitized_field_name:

        def getitem(obj, field_name: str):
            try:
                return getattr(obj, field_name)
            except (AttributeError, ObjectDoesNotExist):
                return None

        return reduce(getitem, sanitized_field_name.split("."), instance)
    else:
        return getattr(instance, sanitize_field_name(instance, sanitized_field_name))
