import typing
from dataclasses import Field
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

try:
    from typing import _TypingBase as typing_base  # type: ignore
except ImportError:
    from typing import _Final as typing_base  # type: ignore


AnnotatedTypeNames = {"AnnotatedMeta", "_AnnotatedAlias"}
_GenericAlias = getattr(typing, "_GenericAlias")
EMPTY = object()


def get_origin_type(type_name: Type) -> Optional[Type]:
    return getattr(type_name, "__origin__", None)


def get_type_args(type_name: Type) -> List[Type]:
    return getattr(type_name, "__args__", [])


def is_optional(type_name: Type) -> bool:
    return (
        get_origin_type(type_name) is Union
        and bool(get_type_args(type_name))
        and get_type_args(type_name)[-1] is type(None)
    )


def get_type_parameters(type_name: Type) -> List[Type]:
    return getattr(get_origin_type(type_name), "__parameters__", [])


def get_parameters_map(type_name: Type) -> Dict[Type, Type]:
    args = get_type_args(type_name)
    parameters = get_type_parameters(type_name)

    return dict(zip(parameters, args))


def get_dataclass_fields(type_name: Type) -> Dict[str, Field]:
    return getattr(type_name, "__dataclass_fields__", {})


def unpack_optional(type_name: Type) -> Type:
    return get_type_args(type_name)[0]


def is_enum_type(type_name: Type) -> bool:
    return issubclass(type_name, Enum)


def is_named_tuple(type_name: Type) -> bool:
    return issubclass(type_name, tuple) and hasattr(type_name, "_fields")


def is_typed_dict(type_name: Type) -> bool:
    return issubclass(type_name, dict) and hasattr(type_name, "__annotations__")


def map_generic_type(type_name: Any, type_map: Dict[Any, Any]) -> Any:
    if not type_map:
        return type_name

    type_args = get_type_args(type_name)
    origin_type = get_origin_type(type_name)

    if origin_type is None:  # not a generic type
        return type_name

    if type_args:
        mapped_args = tuple([type_map[arg] for arg in type_args])
        return _GenericAlias(origin_type, mapped_args)

    return type_name
