from __future__ import annotations

import collections
import datetime
import decimal
import re
import typing
from abc import abstractmethod
from base64 import b64decode
from enum import Enum
from functools import lru_cache
from inspect import isclass
from ipaddress import IPv4Address, IPv6Address
from pathlib import Path, PosixPath, PurePath, PurePosixPath, PureWindowsPath, WindowsPath
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Pattern,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    final,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from chili.typing import (
    _DECODABLE,
    _DECODE_MAPPER,
    _PROPERTIES,
    UNDEFINED,
    TypeSchema,
    create_schema,
    get_origin_type,
    get_parameters_map,
    get_type_args,
    is_class,
    is_dataclass,
    is_decodable,
    is_enum_type,
    is_named_tuple,
    is_newtype,
    is_optional,
    is_typed_dict,
    is_user_string,
    map_generic_type,
    resolve_forward_reference,
    unpack_optional,
)

from .error import DecoderError
from .iso_datetime import parse_iso_date, parse_iso_datetime, parse_iso_duration, parse_iso_time
from .mapper import Mapper
from .state import StateObject

C = TypeVar("C")
U = TypeVar("U")
T = TypeVar("T")
E = TypeVar("E", bound=Enum)


class TypeDecoder(Protocol):
    @abstractmethod
    def decode(self, value):
        ...


@final
class SimpleDecoder(Generic[T]):
    def __init__(self, func: Callable[[Any], T]) -> None:
        self._decoder = func

    def decode(self, value: Any) -> T:
        return self._decoder(value)


@final
class ProxyDecoder(Generic[T]):
    def __init__(self, type_annotation: Any) -> None:
        self._decoder = build_type_decoder(type_annotation)

    def decode(self, value: Any) -> T:
        return self._decoder.decode(value)


_REGEX_FLAGS = {
    "i": re.I,
    "m": re.M,
    "s": re.S,
    "x": re.X,
}


def decode_regex_from_string(value: str) -> Pattern:
    """
    Decodes regex from string containing flags /ims.
    """
    if value.startswith("/"):
        if value.endswith("/"):
            return re.compile(value[1:-1])
        elif value[-2] == "/":
            pattern = value[1:-2]
            flags = value[-1]
        elif value[-3] == "/":
            pattern = value[1:-3]
            flags = value[-2:]
        elif value[-4] == "/":
            pattern = value[1:-4]
            flags = value[-3:]
        elif value[-5] == "/":
            pattern = value[1:-5]
            flags = value[-4:]
        else:
            raise DecoderError.invalid_input(value)
    else:
        return re.compile(value)

    return re.compile(pattern, flags=sum(_REGEX_FLAGS[flag] for flag in flags))


def decodable(_cls=None, mapper: Optional[Mapper] = None) -> Any:
    def _decorate(cls) -> Type[C]:
        # Attach schema to make the class decodable
        if not hasattr(cls, _PROPERTIES):
            setattr(cls, _PROPERTIES, create_schema(cls))
            if mapper:
                setattr(cls, _DECODE_MAPPER, mapper)

            inner_classes = [
                icls
                for icls in cls.__dict__.values()
                if isclass(icls) and icls.__module__ == cls.__module__ and not hasattr(icls, _PROPERTIES)
            ]
            for inner_class in inner_classes:
                _decorate(inner_class)

        setattr(cls, _DECODABLE, True)

        return cls

    if _cls is None:
        return _decorate

    return _decorate(_cls)


class TypeDecoders(Dict[Any, TypeDecoder]):
    def __hash__(self) -> int:  # type: ignore
        return hash(tuple(sorted([str(key) for key in self.keys()])))


def ordered_dict(value: List[List[Any]]) -> collections.OrderedDict:
    result = collections.OrderedDict()
    for item in value:
        result[item[0]] = item[1]

    return result


_builtin_type_decoders = TypeDecoders(
    {
        bool: SimpleDecoder[bool](bool),
        int: SimpleDecoder[int](int),
        float: SimpleDecoder[float](float),
        str: SimpleDecoder[str](str),
        bytes: SimpleDecoder[bytes](lambda value: b64decode(value.encode("utf8"))),
        bytearray: SimpleDecoder[bytearray](lambda value: bytearray(b64decode(value.encode("utf8")))),
        list: SimpleDecoder[list](list),
        set: SimpleDecoder[set](set),
        frozenset: SimpleDecoder[frozenset](frozenset),
        tuple: SimpleDecoder[tuple](tuple),
        dict: SimpleDecoder[dict](dict),
        collections.OrderedDict: SimpleDecoder[collections.OrderedDict](ordered_dict),
        collections.deque: SimpleDecoder[collections.deque](collections.deque),
        typing.TypedDict: SimpleDecoder[typing.TypedDict](typing.TypedDict),  # type: ignore
        typing.Dict: SimpleDecoder[dict](dict),
        typing.List: SimpleDecoder[list](list),
        typing.Sequence: SimpleDecoder[list](list),
        typing.Tuple: SimpleDecoder[tuple](tuple),  # type: ignore
        typing.Set: SimpleDecoder[set](set),
        typing.FrozenSet: SimpleDecoder[frozenset](frozenset),
        typing.Deque: SimpleDecoder[typing.Deque](typing.Deque),
        typing.AnyStr: SimpleDecoder[str](str),  # type: ignore
        decimal.Decimal: SimpleDecoder[decimal.Decimal](decimal.Decimal),
        datetime.time: SimpleDecoder[datetime.time](parse_iso_time),
        datetime.date: SimpleDecoder[datetime.date](parse_iso_date),
        datetime.datetime: SimpleDecoder[datetime.datetime](parse_iso_datetime),
        datetime.timedelta: SimpleDecoder[datetime.timedelta](parse_iso_duration),
        PurePath: SimpleDecoder[PurePath](PurePath),
        PureWindowsPath: SimpleDecoder[PureWindowsPath](PureWindowsPath),
        PurePosixPath: SimpleDecoder[PurePosixPath](PurePosixPath),
        Path: SimpleDecoder[Path](Path),
        PosixPath: SimpleDecoder[PosixPath](PosixPath),
        WindowsPath: SimpleDecoder[WindowsPath](WindowsPath),
        Pattern: SimpleDecoder[Pattern](decode_regex_from_string),
        re.Pattern: SimpleDecoder[re.Pattern](decode_regex_from_string),
        IPv4Address: SimpleDecoder[IPv4Address](IPv4Address),
        IPv6Address: SimpleDecoder[IPv6Address](IPv6Address),
        UUID: SimpleDecoder[UUID](UUID),
    }
)


class ListDecoder(TypeDecoder):
    def __init__(self, item_decoder: TypeDecoder):
        self.item_decoder = item_decoder

    def decode(self, value: list) -> list:
        res = []
        for item in value:
            decoded = self.item_decoder.decode(item)
            res.append(decoded)

        return res


class TupleDecoder(TypeDecoder):
    def __init__(self, items_decoder: List[Union[TypeDecoder, Any]]):
        self.items_decoder = items_decoder
        self._variadic = items_decoder[-1] is Ellipsis

    def decode(self, value: Sequence) -> Tuple:
        if self._variadic:
            return self._decode_variadic(value)
        return self._decode_static(value)

    def _decode_variadic(self, value: Sequence) -> Tuple:
        result = []
        type_decoders = self.items_decoder[:-1]
        num_decoders = len(type_decoders)

        for index, item in enumerate(value):
            decoder = type_decoders[min(index, num_decoders - 1)]
            result.append(decoder.decode(item))

        return tuple(result)

    def _decode_static(self, value: Sequence) -> Tuple:
        result = [decoder.decode(value[index]) for index, decoder in enumerate(self.items_decoder)]
        return tuple(result)


class DictDecoder(TypeDecoder):
    def __init__(self, encoders: List[TypeDecoder]) -> None:
        self.key_decoder, self.value_decoder = encoders

    def decode(self, value: dict) -> dict:
        return {self.key_decoder.decode(i_key): self.value_decoder.decode(i_value) for i_key, i_value in value.items()}


class OrderedDictDecoder(TypeDecoder):
    def __init__(self, decoders: List[TypeDecoder]):
        self.key_decoder, self.value_decoder = decoders

    def decode(self, value: list) -> collections.OrderedDict:
        result = collections.OrderedDict()

        for item in value:
            result[self.key_decoder.decode(item[0])] = self.value_decoder.decode(item[1])

        return result


class UnionDecoder(TypeDecoder):
    _PRIMITIVE_TYPES = {int, float, bool, str}
    _TRANSFORMABLE_TYPES = {
        datetime.time,
        datetime.datetime,
        datetime.timedelta,
        bytes,
        bytearray,
    }
    _CASTABLES_TYPES = {decimal.Decimal}

    def __init__(self, valid_types: List[Type]):
        self.valid_types = valid_types
        self._type_decoders = {}

        for a_type in valid_types:
            if a_type in self._PRIMITIVE_TYPES:
                self._type_decoders[a_type] = a_type
                continue
            self._type_decoders[a_type] = build_type_decoder(a_type)  # type: ignore

    def decode(self, value: Any) -> Any:
        passed_type = type(value)

        if passed_type in self._PRIMITIVE_TYPES:
            return self._type_decoders.get(passed_type, str)(value)

        if passed_type in {int, str}:
            for castable, decoder in self._type_decoders.items():
                try:
                    return castable(value)
                except Exception:
                    continue

        if passed_type is str:
            for transformable, decoder in self._type_decoders.items():
                try:
                    return decoder.decode(value)
                except Exception:
                    continue

        if passed_type is dict:
            value_keys = value.keys()
            for decodable, decoder in self._type_decoders.items():
                try:
                    if not is_decodable(decodable) and value_keys == get_type_hints(decodable).keys():
                        return decoder.decode(value)
                    if is_decodable(decodable) and value_keys == getattr(decodable, _PROPERTIES, {}).keys():
                        return decoder.decode(value)
                except Exception:
                    continue

        raise DecoderError.invalid_input(value)


class ClassDecoder(TypeDecoder):
    _fields: Dict[str, TypeDecoder]
    _schema: TypeSchema

    def __init__(self, class_name: Type, extra_decoders: TypeDecoders = None):
        self.class_name = class_name
        self._schema = create_schema(class_name)  # type: ignore
        self._extra_decoders = extra_decoders

    def decode(self, value: StateObject) -> Any:
        if not isinstance(value, dict):
            raise DecoderError.invalid_input

        if not hasattr(self, "_fields"):
            self._fields = self._build()

        instance = self.class_name.__new__(self.class_name)  # type: ignore

        for key, prop in self._schema.items():
            prop_value = (
                self._fields[key].decode(value[key]) if key in value else getattr(prop, "default_value", UNDEFINED)
            )
            if prop_value is not UNDEFINED:
                setattr(instance, key, prop_value)

        if hasattr(instance, "__post_init__"):
            instance.__post_init__()

        return instance

    def _build(self) -> Dict[str, TypeDecoder]:
        return {name: self._build_type_decoder(field.type) for name, field in self._schema.items()}

    def _build_type_decoder(self, a_type: Type) -> TypeDecoder:
        return build_type_decoder(a_type, self._extra_decoders, self.class_name.__module__)  # type: ignore


class GenericClassDecoder(ClassDecoder):
    def __init__(self, class_name: Type, extra_decoders: TypeDecoders = None):
        self._generic_type = class_name
        self._generic_parameters = get_parameters_map(class_name)
        self._extra_decoders = extra_decoders
        type_: Type = get_origin_type(class_name)  # type: ignore
        super().__init__(type_)

    def _build_type_decoder(self, a_type: Type) -> TypeDecoder:
        return build_type_decoder(
            map_generic_type(a_type, self._generic_parameters),
            self._extra_decoders,
            self._generic_type.__module__,
        )


class EnumDecoder(TypeDecoder, Generic[E]):
    def __init__(self, class_name: Type):
        self.class_name = class_name

    def decode(self, value: Any) -> E:
        return self.class_name(value)


class NamedTupleDecoder(TypeDecoder):
    def __init__(self, class_name: Type, extra_decoders: TypeDecoders = None):
        self.class_name = class_name
        self._is_typed = hasattr(class_name, "__annotations__")
        self._arg_decoders: List[TypeDecoder] = []
        self._extra_decoders = extra_decoders
        if self._is_typed:
            self._build()

    def decode(self, value: list) -> tuple:
        if not self._is_typed:
            return tuple(value)

        decoded_values = []
        for index, item in enumerate(value):
            if index < len(self._arg_decoders):
                decoded_values.append(self._arg_decoders[index].decode(item))
                continue

            decoded_values.append(item)

        return tuple(decoded_values)

    def _build(self) -> None:
        field_types = self.class_name.__annotations__
        for item_type in field_types.values():
            self._arg_decoders.append(build_type_decoder(item_type, self._extra_decoders, self.class_name.__module__))


class TypedDictDecoder(TypeDecoder):
    def __init__(self, class_name: Type, extra_decoders: TypeDecoders = None):
        self.class_name = class_name
        self._key_decoders = {}
        self._extra_decoders = extra_decoders
        for key_name, key_type in class_name.__annotations__.items():
            self._key_decoders[key_name] = build_type_decoder(key_type, self._extra_decoders, class_name.__module__)

    def decode(self, value: dict) -> dict:
        return {key: self._key_decoders[key].decode(item) for key, item in value.items()}


class OptionalTypeDecoder(TypeDecoder):
    def __init__(self, type_decoder: TypeDecoder):
        self._decoder = type_decoder

    def decode(self, value: Any) -> Any:
        if value is None:
            return None

        return self._decoder.decode(value)


_supported_generics = {
    list: ListDecoder,
    tuple: TupleDecoder,
    dict: DictDecoder,
    set: ListDecoder,
    frozenset: ListDecoder,
    collections.deque: ListDecoder,
    collections.OrderedDict: OrderedDictDecoder,
}


@lru_cache(maxsize=None)
def build_type_decoder(
    a_type: Type, extra_decoders: TypeDecoders = None, module: Any = None, force: bool = False
) -> TypeDecoder:
    if extra_decoders and a_type in extra_decoders:
        return extra_decoders[a_type]

    if a_type in _builtin_type_decoders:
        return _builtin_type_decoders[a_type]

    origin_type = get_origin_type(a_type)

    if origin_type is None and is_dataclass(a_type):
        if issubclass(a_type, Generic):  # type: ignore
            raise DecoderError.invalid_type
        return ClassDecoder(a_type, extra_decoders)

    if origin_type and is_dataclass(origin_type):
        if issubclass(origin_type, Generic):  # type: ignore
            return GenericClassDecoder(a_type)
        return ClassDecoder(a_type, extra_decoders)

    if origin_type is None:
        origin_type = a_type

    if is_class(origin_type) and is_enum_type(origin_type):
        return EnumDecoder(origin_type)

    if is_class(origin_type) and is_named_tuple(origin_type):
        return NamedTupleDecoder(origin_type, extra_decoders)

    if is_class(origin_type) and is_typed_dict(origin_type):
        return TypedDictDecoder(origin_type, extra_decoders)

    if is_class(origin_type) and is_user_string(origin_type):
        return SimpleDecoder[origin_type](origin_type)  # type: ignore

    if origin_type is Union:
        type_args = get_type_args(a_type)
        if len(type_args) == 2 and type_args[-1] is type(None):  # type: ignore
            return OptionalTypeDecoder(
                build_type_decoder(a_type=type_args[0], extra_decoders=extra_decoders)  # type: ignore
            )
        return UnionDecoder(type_args)

    if isinstance(a_type, typing.ForwardRef) and module is not None:
        resolved_reference = resolve_forward_reference(module, a_type)
        if resolved_reference is not None:
            return Decoder[resolved_reference](decoders=extra_decoders)  # type: ignore

    if isinstance(a_type, TypeVar):
        if a_type.__bound__ is None:
            raise DecoderError.invalid_type(a_type)
        return build_type_decoder(a_type.__bound__, extra_decoders, module)

    if is_newtype(a_type):
        return build_type_decoder(a_type.__supertype__, extra_decoders, module)

    if get_origin(origin_type) is not None:
        raise DecoderError.invalid_type(a_type)

    if hasattr(origin_type, _PROPERTIES):
        return Decoder[origin_type](decoders=extra_decoders)  # type: ignore

    if is_optional(a_type):
        return OptionalTypeDecoder(build_type_decoder(unpack_optional(a_type)))  # type: ignore

    if origin_type not in _supported_generics:
        if force and is_class(origin_type):
            return Decoder[origin_type](extra_decoders)  # type: ignore
        raise DecoderError.invalid_type(a_type)

    type_attributes: List[Union[TypeDecoder, Any]] = [
        build_type_decoder(subtype, extra_decoders=extra_decoders, module=module)  # type: ignore
        if subtype is not ...
        else ...
        for subtype in get_type_args(a_type)
    ]
    if len(type_attributes) == 1:
        return _supported_generics[origin_type](type_attributes[0])  # type: ignore

    return _supported_generics[origin_type](type_attributes)  # type: ignore


class Decoder(Generic[T]):
    __generic__: Type[T]
    _decoders: Dict[str, TypeDecoder]

    def __init__(self, decoders: Union[TypeDecoders, Dict[Any, TypeDecoder]] = None, mapper: Optional[Mapper] = None):
        if decoders and not isinstance(decoders, TypeDecoders):
            decoders = TypeDecoders(decoders)
        self.decode_mapper = mapper
        self.type_decoders = decoders

    @property
    def schema(self) -> TypeSchema:
        return getattr(self.__generic__, _PROPERTIES)

    def decode(self, obj: Dict[str, StateObject]) -> T:
        if not hasattr(self, "_decoders"):
            self._decoders = self._build_decoders()

        instance = self.__generic__.__new__(self.__generic__)

        if hasattr(self.__generic__, _DECODE_MAPPER):
            mapper = getattr(self.__generic__, _DECODE_MAPPER)
            obj = mapper.map(obj)
        elif self.decode_mapper:
            obj = self.decode_mapper.map(obj)

        for key, prop in self.schema.items():
            if key not in obj:
                if is_optional(prop.type):
                    value = prop.default_value
                else:
                    raise DecoderError.missing_property(key=key)
            else:
                value = self._decoders[prop.name].decode(obj[key])

            try:
                setattr(instance, prop.name, value)
            except AttributeError:
                setattr(instance, f"_{prop.name}", value)

        return instance

    def _build_decoders(self) -> Dict[str, TypeDecoder]:
        schema: TypeSchema = getattr(self.__generic__, _PROPERTIES)

        return {
            prop.name: build_type_decoder(prop.type, extra_decoders=self.type_decoders, force=True)  # type: ignore
            for prop in schema.values()
        }

    @classmethod
    def __class_getitem__(cls, item: Type) -> Type[Decoder]:  # noqa: E501
        if not isclass(item):
            raise DecoderError.invalid_generic_type

        if is_dataclass(item):
            item = decodable(item)

        if not hasattr(item, _DECODABLE):
            item = decodable(item)

        return type(  # type: ignore
            f"{cls.__qualname__}[{item.__module__}.{item.__qualname__}]",
            tuple([cls]),
            {
                "__generic__": item,
            },
        )


def decode(
    obj: StateObject, a_type: Type[T], decoders: Union[TypeDecoders, Dict[Any, TypeDecoder]] = None, force: bool = False
) -> T:
    if decoders and not isinstance(decoders, TypeDecoders):
        decoders = TypeDecoders(decoders)

    decoder = build_type_decoder(a_type, extra_decoders=decoders, force=force)  # type: ignore
    if decoder is None:
        raise DecoderError.invalid_type

    return decoder.decode(obj)
