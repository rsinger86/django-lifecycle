from .django_info import IS_GTE_1_POINT_9

__version__ = "1.0.2"
__author__ = "Robert Singer"
__author_email__ = "robertgsinger@gmail.com"


class NotSet(object):
    pass


from .decorators import hook
from .hooks import *
from .mixins import LifecycleModelMixin

if IS_GTE_1_POINT_9:
    from .models import LifecycleModel

    pass
