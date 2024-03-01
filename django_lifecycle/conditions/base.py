from __future__ import annotations

import operator
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Union

from .. import types


@dataclass
class ChainedCondition:
    def __init__(
        self,
        left: types.Condition,
        right: types.Condition,
        operator: Callable[[Any, Any], bool],
    ):
        self.left = left
        self.right = right
        self.operator = operator

    def __and__(self, other):
        return ChainedCondition(self, other, operator=operator.and_)

    def __or__(self, other):
        return ChainedCondition(self, other, operator=operator.or_)

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        left_result = self.left(instance, update_fields)
        right_result = self.right(instance, update_fields)
        return self.operator(left_result, right_result)


class ChainableCondition:
    """Base class for defining chainable conditions using `&` and `|`"""

    def __and__(self, other) -> ChainedCondition:
        return ChainedCondition(self, other, operator=operator.and_)

    def __or__(self, other) -> ChainedCondition:
        return ChainedCondition(self, other, operator=operator.or_)

    def __call__(self, instance: Any, update_fields: Union[Iterable[str], None] = None) -> bool:
        ...
