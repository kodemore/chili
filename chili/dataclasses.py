from dataclasses import is_dataclass
from typing import Any, Dict, Type, TypeVar, Union, Callable

from .hydration import hydrate, extract

T = TypeVar("T")


def init_dataclass(data: Dict[str, Any], dataclass: Type[T], mapping: Union[Callable, Dict, str] = None) -> T:
    return hydrate(data, dataclass, strict=False, mapping=mapping)


def asdict(data: Any, mapping: Union[Callable, Dict, str] = None) -> Dict[str, Any]:
    if not is_dataclass(data):
        raise TypeError(f"Can extract only dataclasses, passed `{type(data)}` type instead.")

    return extract(data, strict=False, mapping=mapping)
