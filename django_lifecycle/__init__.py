__version__ = "1.2.2"
__author__ = "Robert Singer"
__author_email__ = "robertgsinger@gmail.com"

from .decorators import hook
from .hooks import AFTER_CREATE
from .hooks import AFTER_DELETE
from .hooks import AFTER_SAVE
from .hooks import AFTER_UPDATE
from .hooks import BEFORE_CREATE
from .hooks import BEFORE_DELETE
from .hooks import BEFORE_SAVE
from .hooks import BEFORE_UPDATE
from .mixins import LifecycleModelMixin
from .models import LifecycleModel


class NotSet(object):
    pass


__all__ = [
    "hook",
    "LifecycleModelMixin",
    "LifecycleModel",
    "BEFORE_SAVE",
    "AFTER_SAVE",
    "BEFORE_CREATE",
    "AFTER_CREATE",
    "BEFORE_UPDATE",
    "AFTER_UPDATE",
    "BEFORE_DELETE",
    "AFTER_DELETE",
    "NotSet",
]
