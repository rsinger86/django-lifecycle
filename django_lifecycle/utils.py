from typing import List

from django.utils.functional import cached_property

from .django_info import DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES


def _get_model_property_names(instance) -> List[str]:
    """
        Gather up properties and cached_properties which may be methods
        that were decorated. Need to inspect class versions b/c doing
        getattr on them could cause unwanted side effects.
    """
    property_names = []

    for name in dir(instance):
        try:
            attr = getattr(type(instance), name)

            if isinstance(attr, property) or isinstance(attr, cached_property):
                property_names.append(name)

        except AttributeError:
            pass

    return property_names


def _get_model_descriptor_names(instance) -> List[str]:
    """
    Attributes which are Django descriptors. These represent a field
    which is a one-to-many or many-to-many relationship that is
    potentially defined in another model, and doesn't otherwise appear
    as a field on this model.
    """

    descriptor_names = []

    for name in dir(instance):
        try:
            attr = getattr(type(instance), name)

            if isinstance(attr, DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES):
                descriptor_names.append(name)
        except AttributeError:
            pass

    return descriptor_names


def _get_field_names(instance) -> List[str]:
    return [field.name for field in instance._meta.get_fields()]


def get_unhookable_attribute_names(instance) -> List[str]:
    return (
        _get_field_names(instance)
        + _get_model_descriptor_names(instance)
        + _get_model_property_names(instance)
        + ["_run_hooked_methods"]
    )
