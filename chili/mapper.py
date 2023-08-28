from collections import namedtuple
from collections.abc import Iterable
from typing import Any, Callable, Dict, Union

from chili.error import MapperError

KeyScheme = namedtuple("KeyScheme", "key scheme")
MappingScheme = Dict[Union[str, Any], Union[Dict, str, Callable, KeyScheme]]


class Mapper:
    def __init__(self, scheme: Union[MappingScheme], preserve_keys: bool = False):
        self.scheme = scheme
        self.preserve_keys = preserve_keys

    def map(self, data: Dict[str, Any], skip_keys: bool = False, default_value: Any = None) -> Dict[str, Any]:
        return self._map(data, self.scheme, skip_keys, default_value)

    def _map(
        self,
        data: Dict,
        scheme: MappingScheme,
        skip_keys: bool,
        default_value: Any = None,
    ) -> Any:
        result = {}
        evaluated_keys = set()
        for new_key, old_key in scheme.items():
            k_type = type(old_key)

            if new_key is Ellipsis:
                map_key = callable(old_key)
                if k_type not in (int, bool) and not map_key:
                    raise MapperError.invalid_schema

                for key, value in data.items():
                    if key in evaluated_keys:
                        continue
                    evaluated_keys.add(key)

                    if map_key:
                        key, value = old_key(key, value)  # type: ignore
                    result[key] = value
                continue
            elif k_type is int or k_type is bool:
                if old_key:
                    evaluated_keys.add(old_key)
                    if skip_keys and old_key not in data:
                        continue
                    result[new_key] = data.get(new_key, default_value)
                continue
            elif k_type is str:
                evaluated_keys.add(old_key)
                if skip_keys and old_key not in data:
                    continue
                result[new_key] = data.get(old_key, default_value)
                continue
            elif k_type is KeyScheme:
                if skip_keys and old_key.key not in data:  # type: ignore
                    continue
                value = data.get(old_key.key, default_value)  # type: ignore
                item_scheme = old_key.scheme  # type: ignore
            elif k_type is dict:
                if skip_keys and new_key not in data:
                    continue
                value = data.get(new_key, default_value)
                item_scheme = old_key
            elif callable(old_key):
                evaluated_keys.add(old_key)
                result[new_key] = old_key(data)
                continue
            else:
                raise MapperError.invalid_schema

            if callable(item_scheme):
                result[new_key] = item_scheme(value)
                continue
            elif isinstance(value, dict):
                result[new_key] = self._map(value, item_scheme, skip_keys, default_value)
                continue
            elif isinstance(value, Iterable):
                result[new_key] = [self._map(item, item_scheme, skip_keys, default_value) for item in iter(value)]
                continue
            else:
                raise MapperError.invalid_value
        if self.preserve_keys:
            return {**{key: value for key, value in data.items() if key not in evaluated_keys}, **result}
        return result
