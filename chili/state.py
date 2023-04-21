from __future__ import annotations

from typing import Dict, Union

StatefulTypes = Union[list, str, int, float, bool, Dict[str, "StatefulTypes"], tuple]  # type: ignore

StateObject = Union[None, StatefulTypes, Dict[str, StatefulTypes]]  # type: ignore[misc]
