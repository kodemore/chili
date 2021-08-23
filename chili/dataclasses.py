from dataclasses import is_dataclass
from typing import Any, Dict, Type, TypeVar

from .hydration import hydrate, extract

T = TypeVar("T")


def init_dataclass(data: Dict[str, Any], dataclass: Type[T]) -> T:
    return hydrate(data, dataclass, strict=False)


def asdict(data: Any) -> Dict[str, Any]:
    if not is_dataclass(data):
        raise TypeError(f"Can extract only dataclasses, passed `{type(data)}` type instead.")

    return extract(data, strict=False)
