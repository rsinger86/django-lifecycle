from distutils.version import StrictVersion

import django

DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES = []

if StrictVersion(django.__version__) < StrictVersion("1.9"):
    from django.db.models.fields.related import (
        SingleRelatedObjectDescriptor,
        ReverseSingleRelatedObjectDescriptor,
        ForeignRelatedObjectsDescriptor,
        ManyRelatedObjectsDescriptor,
        ReverseManyRelatedObjectsDescriptor,
    )

    DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES.extend(
        [
            SingleRelatedObjectDescriptor,
            ReverseSingleRelatedObjectDescriptor,
            ForeignRelatedObjectsDescriptor,
            ManyRelatedObjectsDescriptor,
            ReverseManyRelatedObjectsDescriptor,
        ]
    )

if StrictVersion(django.__version__) >= StrictVersion("1.9"):
    from django.db.models.fields.related_descriptors import (
        ForwardManyToOneDescriptor,
        ReverseOneToOneDescriptor,
        ReverseManyToOneDescriptor,
        ManyToManyDescriptor,
    )

    DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES.extend(
        [
            ForwardManyToOneDescriptor,
            ReverseOneToOneDescriptor,
            ReverseManyToOneDescriptor,
            ManyToManyDescriptor,
        ]
    )

if StrictVersion(django.__version__) >= StrictVersion("1.11"):
    from django.db.models.fields.related_descriptors import ForwardOneToOneDescriptor

    DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES.extend([ForwardOneToOneDescriptor])


DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES = tuple(DJANGO_RELATED_FIELD_DESCRIPTOR_CLASSES)
IS_GTE_1_POINT_9 = StrictVersion(django.__version__) >= StrictVersion("1.9")
