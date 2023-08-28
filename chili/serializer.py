from __future__ import annotations

from typing import Any, Generic, Type, TypeVar

from chili.decoder import Decoder
from chili.encoder import Encoder
from chili.error import SerialisationError
from chili.typing import (
    _DECODABLE,
    _ENCODABLE,
    _PROPERTIES,
    _USE_INIT,
    create_schema,
    create_schema_from_init,
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


def serializable(_cls=None, use_init: bool = False) -> Any:
    def _decorate(cls) -> Type[C]:
        if not hasattr(cls, _PROPERTIES):
            if use_init:
                setattr(cls, _PROPERTIES, create_schema_from_init(cls))
                setattr(cls, _USE_INIT, True)
            else:
                setattr(cls, _PROPERTIES, create_schema(cls))

        setattr(cls, _DECODABLE, True)
        setattr(cls, _ENCODABLE, True)

        return cls

    if _cls is None:
        return _decorate

    return _decorate(_cls)
