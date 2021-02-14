from .django_info import IS_GTE_1_POINT_9

__version__ = "0.8.1"
__author__ = "Robert Singer"
__author_email__ = "robertgsinger@gmail.com"


class NotSet(object):
    pass


from .decorators import hook
from .mixins import LifecycleModelMixin
from .hooks import *


if IS_GTE_1_POINT_9:
    from .models import LifecycleModel
