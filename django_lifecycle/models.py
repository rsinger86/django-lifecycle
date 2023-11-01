from django.db import models

from .mixins import LifecycleModelMixin


class LifecycleModel(LifecycleModelMixin, models.Model):
    class Meta:
        abstract = True
