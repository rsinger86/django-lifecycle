from functools import wraps
from typing import Set

from django.db.models.base import ModelBase


def _get_field_names(klass: ModelBase) -> Set[str]:
    names = set()

    for f in klass._meta.get_fields():
        names.add(f.name)

        if klass._meta.get_field(f.name).get_internal_type() == "ForeignKey":
            # TODO: not robust for cases with custom Field(db_column=...) definition
            names.add(f.name + "_id")

    return names


def get_unhookable_attribute_names(klass) -> Set[str]:
    return (
            _get_field_names(klass) |
            {'MultipleObjectsReturned', 'DoesNotExist'}
    )


def cached_class_property(getter):
    class CachedClassProperty:
        def __init__(self, f):
            self._f = f
            self._name = f.__name__ + '__' + CachedClassProperty.__name__

        @wraps(getter)
        def __get__(self, instance, cls):
            if not hasattr(cls, self._name):
                setattr(cls, self._name, self._f(cls))
            return getattr(cls, self._name)

    return CachedClassProperty(getter)
