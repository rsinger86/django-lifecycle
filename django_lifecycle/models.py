#
# Django 1.8 requires that also abstract models are registered properly.
# This is not required for Django 1.9+
#

from django.db import models

from .mixins import LifecycleModelMixin


class LifecycleModel(LifecycleModelMixin, models.Model):
    class Meta:
        abstract = True
