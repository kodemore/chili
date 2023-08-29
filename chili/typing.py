from __future__ import annotations

import sys
import typing
from dataclasses import MISSING, Field, InitVar, is_dataclass
from enum import Enum
from inspect import isclass as is_class
from typing import Any, Callable, ClassVar, Dict, List, NewType, Optional, Type, Union

from chili.error import SerialisationError

AnnotatedTypeNames = {"AnnotatedMeta", "_AnnotatedAlias"}
_GenericAlias = getattr(typing, "_GenericAlias")
_PROPERTIES = "__typed_properties__"
_DECODE_MAPPER = "__decode_mapper__"
_ENCODE_MAPPER = "__encode_mapper__"
_ENCODABLE = "__encodable__"
_DECODABLE = "__decodable__"
UNDEFINED = object()


__all__ = [
    "get_class_fields",
    "get_dataclass_fields",
    "get_origin_type",
    "get_parameters_map",
    "get_type_args",
    "get_type_parameters",
    "is_class",
    "is_dataclass",
    "is_enum_type",
    "is_named_tuple",
    "is_optional",
    "is_typed_dict",
    "map_generic_type",
    "unpack_optional",
    "resolve_forward_reference",
    "create_schema",
    "TypeSchema",
    "Property",
]


def get_origin_type(type_name: Type) -> Optional[Type]:
    return getattr(type_name, "__origin__", None)


def get_type_args(type_name: Type) -> List[Type]:
    return getattr(type_name, "__args__", [])


def is_encodable(type_name: Type) -> bool:
    return is_class(type_name) and hasattr(type_name, _ENCODABLE)


def is_decodable(type_name: Type) -> bool:
    return is_class(type_name) and hasattr(type_name, _DECODABLE)


def is_serialisable(type_name: Type) -> bool:
    return is_class(type_name) and hasattr(type_name, _DECODABLE) and hasattr(type_name, _ENCODABLE)


def is_optional(type_name: Type) -> bool:
    return (
        get_origin_type(type_name) is Union
        and bool(get_type_args(type_name))
        and get_type_args(type_name)[-1] is type(None)  # noqa
    )


def is_newtype(type_name: Type) -> bool:
    if not hasattr(type_name, "__qualname__"):
        return False
    if type_name.__qualname__ != "NewType.<locals>.new_type":
        return False

    return True


def get_type_parameters(type_name: Type) -> List[Type]:
    return getattr(get_origin_type(type_name), "__parameters__", [])


def get_parameters_map(type_name: Type) -> Dict[Type, Type]:
    args = get_type_args(type_name)
    parameters = get_type_parameters(type_name)

    return dict(zip(parameters, args))


def get_dataclass_fields(type_name: Type) -> Dict[str, Field]:
    return getattr(type_name, "__dataclass_fields__", {})


def get_class_fields(type_name: Type) -> Dict[str, Field]:
    return getattr(type_name, "__annotations__", {})


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


def resolve_forward_reference(module: Any, ref: Union[typing.ForwardRef, str]) -> Any:
    if isinstance(ref, typing.ForwardRef):
        name = ref.__forward_arg__
    else:
        name = ref
    if name in sys.modules[module].__dict__:
        return sys.modules[module].__dict__[name]

    if name in sys.modules["builtins"].__dict__:
        return sys.modules["builtins"].__dict__[name]

    return None


class Property:
    __slots__ = ("name", "type", "_default_value", "_default_factory")

    def __init__(
        self,
        name: str,
        property_type: Type,
        default_value: Any = UNDEFINED,
        default_factory: Callable = None,
    ):
        self.name = name
        self.type = property_type
        self._default_value = default_value if default_value is not MISSING else UNDEFINED
        self._default_factory = default_factory

    @property
    def default_value(self) -> Any:
        if self._default_value is not UNDEFINED:
            return self._default_value

        if self._default_factory:
            return self._default_factory()

        return None

    def __eq__(self, other: Property) -> bool:  # type: ignore
        return self.name == other.name and self.type is other.type


TypeSchema = NewType("TypeSchema", Dict[str, Property])


_default_factories = (list, dict, tuple, set, bytes, bytearray, frozenset)


def create_schema(cls: Type) -> TypeSchema:
    try:
        properties = typing.get_type_hints(cls, localns=cls.__dict__)  # type: ignore
    except NameError as e:
        raise SerialisationError.invalid_type from e

    schema = TypeSchema({})
    base_classes = [base_class for base_class in cls.__mro__[1:-1] if hasattr(base_class, _PROPERTIES)]
    for base_class in base_classes:
        schema = {**getattr(base_class, _PROPERTIES), **schema}  # type: ignore

    attributes = {name: value for name, value in cls.__dict__.items() if not name.startswith("__")}

    if hasattr(cls, "__dataclass_fields__"):
        for key, value in cls.__dataclass_fields__.items():
            if value.default is not MISSING or value.default_factory is not MISSING:
                attributes[key] = value

    for name, p_type in properties.items():
        p_origin = get_origin_type(p_type)

        if isinstance(p_type, InitVar):
            continue

        # ignore class vars as they are not object properties
        if p_origin and p_origin in (ClassVar, InitVar):
            continue

        if name in attributes:
            prop_value = attributes[name]
            if isinstance(prop_value, Field):
                schema[name] = Property(
                    name,
                    p_type,
                    default_value=prop_value.default,
                    default_factory=prop_value.default_factory,  # type: ignore
                )
            else:
                prop_value_type = type(prop_value)
                if not prop_value and (
                    prop_value_type in _default_factories or isinstance(prop_value, _default_factories)
                ):
                    schema[name] = Property(name, p_type, default_factory=prop_value_type)
                else:
                    schema[name] = Property(name, p_type, default_value=prop_value)
        else:
            schema[name] = Property(name, p_type)

    return schema
