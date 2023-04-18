from json import dumps, loads
from typing import Any, Type, TypeVar, Union, Generic

from .decoder import decode, TypeDecoders, Decoder
from .encoder import encode, TypeEncoders, Encoder
from .serializer import Serializer

T = TypeVar("T")


def json_encode(obj: Any, type_hint: Type = None, type_encoders: TypeEncoders = None) -> str:
    return dumps(encode(obj, type_hint, type_encoders))


def json_decode(json_str: str, type_hint: Type[T], type_decoders: TypeDecoders = None) -> Union[T, Any]:
    return decode(loads(json_str), type_hint, type_decoders)


class JsonEncoder(Encoder, Generic[T]):
    def encode(self, obj: T) -> str:  # type: ignore
        return dumps(super().encode(obj))


class JsonDecoder(Decoder, Generic[T]):
    def decode(self, json_str: str) -> T:  # type: ignore
        return super().decode(loads(json_str))


class JsonSerializer(Serializer, Generic[T]):
    def encode(self, obj: T) -> str:  # type: ignore
        return dumps(super().encode(obj))

    def decode(self, json_str: str) -> T:  # type: ignore
        return super().decode(loads(json_str))
