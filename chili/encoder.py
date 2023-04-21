from __future__ import annotations

import collections
import datetime
import decimal
import typing
from abc import abstractmethod
from base64 import b64encode
from enum import Enum
from functools import lru_cache
from inspect import isclass
from typing import (
    Generic,
    Type,
    Any,
    Dict,
    TypeVar,
    Protocol,
    List,
    Union,
    Callable,
    final,
    Tuple,
)

from chili.typing import (
    create_schema,
    _PROPERTIES,
    _ENCODABLE,
    TypeSchema,
    is_dataclass,
    get_origin_type,
    resolve_forward_reference,
    is_enum_type,
    is_named_tuple,
    is_typed_dict,
    get_parameters_map,
    map_generic_type,
    is_optional,
    get_type_args,
    unpack_optional,
    is_newtype,
    UNDEFINED,
    is_class,
)
from .error import EncoderError
from .iso_datetime import timedelta_to_iso_duration
from .state import StateObject

C = TypeVar("C")
U = TypeVar("U")
T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class TypeEncoder(Protocol):
    @abstractmethod
    def encode(self, value):
        ...


@final
class ProxyEncoder(TypeEncoder, Generic[T]):
    def __init__(self, func: Callable[[Any], T]):
        self._encoder = func

    def encode(self, value: Any) -> T:
        return self._encoder(value)


def encodable(_cls=None) -> Any:
    def _decorate(cls) -> Type[C]:
        # Attach schema to make the class encodable
        if not hasattr(cls, _PROPERTIES):
            setattr(cls, _PROPERTIES, create_schema(cls))

        setattr(cls, _ENCODABLE, True)

        return cls

    if _cls is None:
        return _decorate

    return _decorate(_cls)


class TypeEncoders(Dict[Any, TypeEncoder]):
    def __hash__(self) -> int:  # type: ignore[override]
        return hash(tuple(sorted([str(key) for key in self.keys()])))


def ordered_dict(value: collections.OrderedDict) -> List[List[Any]]:
    result = []
    for i_key, i_value in value.items():
        result.append([i_key, i_value])

    return result


_builtin_type_encoders = TypeEncoders(
    {
        bool: ProxyEncoder[bool](bool),
        int: ProxyEncoder[int](int),
        float: ProxyEncoder[float](float),
        str: ProxyEncoder[str](str),
        bytes: ProxyEncoder[str](lambda value: b64encode(value).decode("utf8")),
        bytearray: ProxyEncoder[str](lambda value: b64encode(value).decode("utf8")),
        list: ProxyEncoder[list](list),
        set: ProxyEncoder[list](list),
        frozenset: ProxyEncoder[list](list),
        tuple: ProxyEncoder[list](list),
        dict: ProxyEncoder[dict](dict),
        collections.OrderedDict: ProxyEncoder[list](ordered_dict),
        collections.deque: ProxyEncoder[list](list),
        typing.TypedDict: ProxyEncoder[dict](dict),  # type: ignore
        typing.Dict: ProxyEncoder[dict](dict),
        typing.List: ProxyEncoder[list](list),
        typing.Sequence: ProxyEncoder[list](list),
        typing.Tuple: ProxyEncoder[list](list),  # type: ignore
        typing.Set: ProxyEncoder[list](list),
        typing.FrozenSet: ProxyEncoder[list](list),
        typing.Deque: ProxyEncoder[list](list),
        typing.AnyStr: ProxyEncoder[str](str),  # type: ignore
        decimal.Decimal: ProxyEncoder[str](str),
        datetime.time: ProxyEncoder[str](lambda value: value.isoformat()),
        datetime.date: ProxyEncoder[str](lambda value: value.isoformat()),
        datetime.datetime: ProxyEncoder[str](lambda value: value.isoformat()),
        datetime.timedelta: ProxyEncoder[str](timedelta_to_iso_duration),
    }
)


class ListEncoder(TypeEncoder):
    def __init__(self, item_encoder: TypeEncoder):
        self.item_encoder = item_encoder

    def encode(self, value: typing.List) -> list:
        return [self.item_encoder.encode(item) for item in value]


class TupleEncoder(TypeEncoder):
    def __init__(self, items_encoder: List[Union[TypeEncoder, Any]]):
        self.items_encoder = items_encoder
        self._variadic = items_encoder[-1] is Ellipsis

    def encode(self, value: Tuple) -> List:
        if self._variadic:
            return self._encode_variadic(value)
        return self._encode_static(value)

    def _encode_variadic(self, value: Tuple) -> List:
        result = []
        type_encoders = self.items_encoder[:-1]
        num_encoders = len(type_encoders)

        for index, item in enumerate(value):
            encoder = type_encoders[min(index, num_encoders - 1)]
            result.append(encoder.encode(item))

        return result

    def _encode_static(self, value: Tuple) -> List:
        result = [encoder.encode(value[index]) for index, encoder in enumerate(self.items_encoder)]
        return result


class DictEncoder(TypeEncoder):
    def __init__(self, encoders: List[TypeEncoder]):
        self.key_encoder, self.value_encoder = encoders

    def encode(self, value: dict) -> dict:
        return {self.key_encoder.encode(i_key): self.value_encoder.encode(i_value) for i_key, i_value in value.items()}


class OrderedDictEncoder(TypeEncoder):
    def __init__(self, encoders: List[TypeEncoder]):
        self.key_encoder, self.value_encoder = encoders

    def encode(self, value: dict) -> list:
        return [
            [self.key_encoder.encode(i_key), self.value_encoder.encode(i_value)] for i_key, i_value in value.items()
        ]


class ClassEncoder(TypeEncoder):
    _fields: Dict[str, TypeEncoder]
    _schema: TypeSchema

    def __init__(self, class_name: Type, extra_encoders: TypeEncoders = None):
        self.class_name = class_name
        self._extra_encoders = extra_encoders
        self._schema = create_schema(class_name)

    def encode(self, value: Any) -> StateObject:
        if not isinstance(value, self.class_name):
            raise EncoderError.invalid_input

        if not hasattr(self, "_fields"):
            self._fields = self._build()

        result = {}
        for name, field in self._schema.items():
            prop_value = self._fields[name].encode(getattr(value, name, field.default_value))
            if prop_value is not UNDEFINED:
                result[name] = prop_value

        return result

    def _build(self) -> Dict[str, TypeEncoder]:
        return {name: self._build_type_encoder(field.type) for name, field in self._schema.items()}

    def _build_type_encoder(self, a_type: Type) -> TypeEncoder:
        return build_type_encoder(a_type, self._extra_encoders, self.class_name.__module__)  # type: ignore


class GenericClassEncoder(ClassEncoder):
    def __init__(self, class_name: Type, extra_encoders: TypeEncoders = None):
        self._generic_type = class_name
        self._extra_encoders = extra_encoders
        self._generic_parameters = get_parameters_map(class_name)
        type_: Type = get_origin_type(class_name)  # type: ignore
        super().__init__(type_)

    def _build_type_encoder(self, a_type: Type) -> TypeEncoder:
        return build_type_encoder(
            map_generic_type(a_type, self._generic_parameters),
            self._extra_encoders,
            self._generic_type.__module__,
        )


class EnumEncoder(TypeEncoder, Generic[E]):
    def __init__(self, enum_type: Type):
        self.enum_type = enum_type

    def encode(self, value: E) -> Any:
        if not isinstance(value, self.enum_type):
            raise EncoderError.invalid_input

        return value.value


class NamedTupleEncoder(TypeEncoder):
    def __init__(self, class_name: Type, extra_encoders: TypeEncoders = None):
        self.type = class_name
        self._is_typed = hasattr(class_name, "__annotations__")
        self._arg_encoders: List[TypeEncoder] = []
        self._extra_encoders = extra_encoders
        if self._is_typed:
            self._build()

    def encode(self, value: tuple) -> list:
        if not self._is_typed:
            return list(value)

        return [
            self._arg_encoders[index].encode(item) if index < len(self._arg_encoders) else item
            for index, item in enumerate(value)
        ]

    def _build(self) -> None:
        field_types = self.type.__annotations__
        for item_type in field_types.values():
            self._arg_encoders.append(build_type_encoder(item_type, self._extra_encoders, self.type.__module__))


class TypedDictEncoder(TypeEncoder):
    def __init__(self, class_name: Type, extra_encoders: TypeEncoders = None):
        self.type = class_name
        self._key_encoders = {}
        for key_name, key_type in class_name.__annotations__.items():
            self._key_encoders[key_name] = build_type_encoder(key_type, extra_encoders, class_name.__module__)

    def encode(self, value: dict) -> dict:
        return {key: self._key_encoders[key].encode(item) for key, item in value.items()}


class OptionalTypeEncoder(TypeEncoder):
    def __init__(self, type_encoder: TypeEncoder):
        self._encoder = type_encoder

    def encode(self, value: Any) -> Any:
        if value is None:
            return None

        return self._encoder.encode(value)


class UnionEncoder(TypeEncoder):
    def __init__(self, supported_types: List[Type], extra_encoders: TypeEncoders = None):
        self.supported_types = supported_types
        self._extra_encoders = extra_encoders

    def encode(self, value: Any) -> Any:
        value_type = type(value)
        if value_type not in self.supported_types:
            raise EncoderError.invalid_input

        return build_type_encoder(value_type, self._extra_encoders).encode(value)  # type: ignore


_supported_generics = {
    list: ListEncoder,
    tuple: TupleEncoder,
    dict: DictEncoder,
    set: ListEncoder,
    frozenset: ListEncoder,
    collections.deque: ListEncoder,
    collections.OrderedDict: OrderedDictEncoder,
}


@lru_cache(maxsize=None)
def build_type_encoder(a_type: Type, extra_encoders: TypeEncoders = None, module: Any = None) -> TypeEncoder:
    if extra_encoders and a_type in extra_encoders:
        return extra_encoders[a_type]

    if a_type in _builtin_type_encoders:
        return _builtin_type_encoders[a_type]

    origin_type = get_origin_type(a_type)

    if origin_type is None and is_dataclass(a_type):
        if issubclass(a_type, Generic):  # type: ignore
            raise EncoderError.invalid_type
        return ClassEncoder(a_type, extra_encoders)

    if origin_type and is_dataclass(origin_type):
        if issubclass(origin_type, Generic):  # type: ignore
            return GenericClassEncoder(a_type)
        return ClassEncoder(a_type, extra_encoders)

    if origin_type is None:
        origin_type = a_type

    if is_class(origin_type) and is_enum_type(origin_type):
        return EnumEncoder(origin_type)

    if is_class(origin_type) and is_named_tuple(origin_type):
        return NamedTupleEncoder(origin_type, extra_encoders)

    if is_class(origin_type) and is_typed_dict(origin_type):
        return TypedDictEncoder(origin_type, extra_encoders)

    if origin_type is Union:
        type_args = get_type_args(a_type)
        if len(type_args) == 2 and type_args[-1] is type(None):
            return OptionalTypeEncoder(build_type_encoder(type_args[0], extra_encoders))  # type: ignore
        return UnionEncoder(type_args, extra_encoders)

    if isinstance(a_type, typing.ForwardRef) and module is not None:
        resolved_reference = resolve_forward_reference(module, a_type)
        if resolved_reference is not None:
            return Encoder[resolved_reference](encoders=extra_encoders)  # type: ignore[valid-type]

    if typing.get_origin(origin_type) is not None:
        raise EncoderError.invalid_type(a_type)

    if hasattr(origin_type, _PROPERTIES):
        if origin_type != a_type:
            return GenericClassEncoder(a_type)
        return Encoder[origin_type](encoders=extra_encoders)  # type: ignore[valid-type]

    if is_optional(a_type):
        return OptionalTypeEncoder(build_type_encoder(unpack_optional(a_type), extra_encoders))  # type: ignore

    if isinstance(a_type, TypeVar):
        if a_type.__bound__ is None:
            raise EncoderError.invalid_type(a_type)
        return build_type_encoder(a_type.__bound__, extra_encoders, module)

    if is_newtype(a_type):
        return build_type_encoder(a_type.__supertype__, extra_encoders, module)

    if origin_type not in _supported_generics:
        raise EncoderError.invalid_type(a_type)

    type_attributes: List[TypeEncoder] = [
        build_type_encoder(subtype, module=module) if subtype is not ... else ...  # type: ignore
        for subtype in get_type_args(a_type)
    ]

    if len(type_attributes) == 1:
        return _supported_generics[origin_type](type_attributes[0])  # type: ignore

    return _supported_generics[origin_type](type_attributes)  # type: ignore


class Encoder(Generic[T]):
    __generic__: Type[T]
    _encoders: Dict[str, TypeEncoder]

    def __init__(self, encoders: Union[Dict, TypeEncoders] = None):
        if encoders and not isinstance(encoders, TypeEncoders):
            encoders = TypeEncoders(encoders)

        self.type_encoders = encoders

    def encode(self, obj: T) -> StateObject:
        if not hasattr(self, "_encoders"):
            self._encoders = self._build_encoders()

        result = {}
        for key, prop in self.schema.items():
            value = getattr(obj, key, prop.default_value)
            if value is UNDEFINED:
                continue
            result[key] = self._encoders[prop.name].encode(value)

        return result

    @property
    def schema(self) -> TypeSchema:
        return getattr(self.__generic__, _PROPERTIES)

    def _build_encoders(self) -> Dict[str, TypeEncoder]:
        schema: TypeSchema = self.schema

        return {
            prop.name: build_type_encoder(prop.type, extra_encoders=self.type_encoders)  # type: ignore
            for prop in schema.values()
        }

    @classmethod
    def __class_getitem__(cls, item: Any) -> Type[Encoder]:  # noqa: E501
        if not isclass(item):
            raise EncoderError.invalid_generic_type

        if is_dataclass(item):
            item = encodable(item)

        if not hasattr(item, _ENCODABLE):
            raise EncoderError.invalid_type

        return type(  # type: ignore
            f"{cls.__qualname__}[{item.__module__}.{item.__qualname__}]",
            tuple([cls]),
            {
                "__generic__": item,
            },
        )


def encode(
    obj: Any,
    type_hint: Type = None,
    encoders: Union[TypeEncoders, Dict[Any, TypeEncoder]] = None,
) -> StateObject:
    if encoders and not isinstance(encoders, TypeEncoders):
        encoders = TypeEncoders(encoders)

    if type_hint is not None:
        encoder = build_type_encoder(type_hint, extra_encoders=encoders)  # type: ignore
    else:
        encoder = build_type_encoder(type(obj), extra_encoders=encoders)  # type: ignore

    if encoder is None:
        raise EncoderError.invalid_input

    return encoder.encode(obj)
