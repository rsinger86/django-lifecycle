from distutils.version import StrictVersion

import django

IS_DJANGO_GTE_1_POINT_9 = StrictVersion(django.__version__) >= StrictVersion("1.9")


class NotSet(object):
    pass


from .decorators import hook
from .mixins import LifecycleModelMixin
from .hooks import *

if IS_DJANGO_GTE_1_POINT_9:
    from .models import LifecycleModel
