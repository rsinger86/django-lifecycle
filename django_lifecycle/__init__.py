from .django_info import IS_GTE_1_POINT_9


class NotSet(object):
    pass


from .decorators import hook
from .mixins import LifecycleModelMixin


if IS_GTE_1_POINT_9:
    from .models import LifecycleModel
