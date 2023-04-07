from __future__ import annotations

from typing import Dict, Union

StatefulTypes = Union[list, str, int, float, bool, dict[str, ...], tuple]  # type: ignore

StateObject = Union[None, StatefulTypes, Dict[str, StatefulTypes]]
