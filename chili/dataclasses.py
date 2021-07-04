from dataclasses import is_dataclass
from typing import Any, Dict, Type, TypeVar

from .hydration import CACHED_HYDRATION_STRATEGIES, get_strategy_for

T = TypeVar("T")


def init_dataclass(data: Dict[str, Any], dataclass: Type[T]) -> T:
    if dataclass in CACHED_HYDRATION_STRATEGIES:
        return CACHED_HYDRATION_STRATEGIES[dataclass].hydrate(data)

    CACHED_HYDRATION_STRATEGIES[dataclass] = get_strategy_for(dataclass)

    return CACHED_HYDRATION_STRATEGIES[dataclass].hydrate(data)


def asdict(data: Any) -> Dict[str, Any]:
    if not is_dataclass(data):
        raise TypeError(f"Can extract only dataclasses, passed `{type(data)}` type instead.")

    strategy = get_strategy_for(type(data))

    return strategy.extract(data)
