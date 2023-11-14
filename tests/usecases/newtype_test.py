import sys
from typing import NewType

from chili import Decoder, Encoder, decodable, encodable


def test_can_encode_newtype_type() -> None:
    # given
    ISBN = NewType("ISBN", str)

    @encodable
    class Book:
        name: str
        isbn: ISBN

        def __init__(self, name: str, isbn: ISBN):
            self.name = name
            self.isbn = isbn

    encoder = Encoder[Book]()
    book = Book("Test", ISBN("1234567890"))

    # when
    result = encoder.encode(book)

    # then
    assert isinstance(result, dict)
    assert result == {"name": "Test", "isbn": "1234567890"}


def test_can_decode_newtype_type() -> None:
    # given
    ISBN = NewType("ISBN", str)

    @decodable
    class Book:
        name: str
        isbn: ISBN

        def __init__(self, name: str, isbn: ISBN):
            self.name = name
            self.isbn = isbn

    decoder = Decoder[Book]()
    book_data = {"name": "Test", "isbn": "1234567890"}

    # when
    result = decoder.decode(book_data)

    # then
    assert isinstance(result, Book)
    assert isinstance(result.isbn, str)
