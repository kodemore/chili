from collections import namedtuple
from collections.abc import Iterable
from typing import Any, Callable, Dict, Union

KeyMapper = namedtuple("KeyMapper", "key scheme")
MappingScheme = Dict[str, Union[Dict, str, Callable]]


class Mapper:
    def __init__(self, scheme: MappingScheme):
        self.scheme = scheme

    def map(self, data) -> Any:
        return self._map(data, self.scheme)

    def _map(self, data: Dict, scheme: MappingScheme) -> Any:
        result = {}
        for new_key, old_key in scheme.items():
            if isinstance(old_key, int):
                if old_key:
                    result[new_key] = data.get(new_key, None)
                continue
            elif isinstance(old_key, str):
                result[new_key] = data.get(old_key, None)
                continue
            elif isinstance(old_key, KeyMapper):
                if old_key.key not in data:
                    result[new_key] = None
                value = data[old_key.key]
                item_scheme = old_key.scheme
            elif isinstance(old_key, dict):
                if new_key not in data:
                    result[new_key] = None
                    continue
                value = data[new_key]
                item_scheme = old_key
            elif callable(old_key):
                result[new_key] = old_key(data)
                continue
            else:
                raise ValueError(
                    f"Unexpected mapping schema passed in `{new_key}`, "
                    f"expected string, callable, bool or instance of KeyMapper."
                )

            if callable(item_scheme):
                result[new_key] = item_scheme(value)
                continue
            elif isinstance(value, dict):
                result[new_key] = self._map(value, item_scheme)
                continue
            elif isinstance(value, Iterable):
                result[new_key] = [self._map(item, item_scheme) for item in iter(value)]
                continue
            else:
                raise ValueError(f"Could not map value {value} with provided scheme {item_scheme}")

        return result


class PersistentMapper(Mapper):
    def _map(self, data: Dict, scheme: MappingScheme) -> Any:
        results = super()._map(data, scheme)
        for key, value in data.items():
            if key not in results:
                results[key] = value
        return results
