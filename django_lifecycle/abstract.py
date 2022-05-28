from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(order=False)
class AbstractHookedMethod(ABC):
    method: Any
    priority: int

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def run(self, instance: Any) -> None:
        ...

    def __lt__(self, other):
        if not isinstance(other, AbstractHookedMethod):
            return NotImplemented

        return self.priority < other.priority
