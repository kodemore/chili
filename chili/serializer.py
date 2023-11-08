from __future__ import annotations

from typing import Any, Generic, Optional, Type, TypeVar

from chili.decoder import Decoder
from chili.encoder import Encoder
from chili.error import SerialisationError
from chili.mapper import Mapper
from chili.typing import (
    _DECODABLE,
    _DECODE_MAPPER,
    _ENCODABLE,
    _ENCODE_MAPPER,
    _PROPERTIES,
    create_schema,
    is_class,
    is_dataclass,
)

C = TypeVar("C")
T = TypeVar("T")


class Serializer(Encoder, Decoder, Generic[T]):
    __generic__: Type[T]

    def __init__(self, type_encoders: Any = None, type_decoders: Any = None):
        Encoder.__init__(self, type_encoders)
        Decoder.__init__(self, type_decoders)

    @classmethod
    def __class_getitem__(cls, item: Type[T]) -> Type[Serializer]:  # noqa: E501
        if not is_class(item):
            raise SerialisationError.invalid_type

        if is_dataclass(item):
            item = serializable(item)

        if not hasattr(item, _DECODABLE) or not hasattr(item, _ENCODABLE):
            raise SerialisationError.invalid_type

        return type(  # type: ignore
            f"{cls.__qualname__}[{item.__module__}.{item.__qualname__}]",
            tuple([cls]),
            {
                "__generic__": item,
            },
        )


def serializable(_cls=None, in_mapper: Optional[Mapper] = None, out_mapper: Optional[Mapper] = None) -> Any:
    def _decorate(cls) -> Type[C]:

        setattr(cls, _PROPERTIES, create_schema(cls))
        if in_mapper is not None:
            setattr(cls, _DECODE_MAPPER, in_mapper)
        if out_mapper is not None:
            setattr(cls, _ENCODE_MAPPER, out_mapper)

        setattr(cls, _DECODABLE, True)
        setattr(cls, _ENCODABLE, True)

        return cls

    if _cls is None:
        return _decorate

    return _decorate(_cls)
