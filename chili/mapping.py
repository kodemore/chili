from collections.abc import Iterable
from typing import Union, Dict, Callable, Any, List

MappingInfo = Dict[str, Union[Dict, str, Callable]]


class MappingStrategy:
    def __init__(self, data: Any, mapping: MappingInfo):
        self.mapping = mapping
        self._data = data

    def map(self) -> Any:
        return self._map(self._data, self.mapping)

    def _map(self, section: Union[List, Dict], mapping: MappingInfo) -> Any:
        if not isinstance(section, dict) and isinstance(section, Iterable):
            return [self._map(item, mapping) for item in iter(section)]

        result = {}
        for key, new_key in mapping.items():
            if key not in section or key == "__name__":
                continue

            if isinstance(new_key, dict):
                if "__name__" in new_key:
                    result[new_key["__name__"]] = self._map(section[key], new_key)
                else:
                    result[key] = self._map(section[key], new_key)
                continue

            if callable(new_key):
                new_key, value = new_key(section[key], self._data)
                result[new_key] = value
                continue

            result[new_key] = section[key]

        return result
