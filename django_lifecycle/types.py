from typing import Any
from typing import Callable
from typing import Iterable
from typing import Union

Condition = Callable[[Any, Union[Iterable[str], None]], bool]
