from dataclasses import is_dataclass
from typing import Any, Dict, Type, TypeVar

from .hydration import extract, hydrate
from .mapping import Mapper

T = TypeVar("T")


def init_dataclass(data: Dict[str, Any], dataclass: Type[T], mapping: Mapper = None) -> T:
    return hydrate(data, dataclass, strict=False, mapping=mapping)


def asdict(data: Any, mapping: Mapper = None) -> Dict[str, Any]:
    if not is_dataclass(data):
        raise TypeError(f"Can extract only dataclasses, passed `{type(data)}` type instead.")

    return extract(data, strict=False, mapping=mapping)
