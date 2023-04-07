import pytest

from chili import decode, encode


def test_fails_to_decode_when_passed_invalid_type() -> None:
    # given
    class Book:
        name: str

    book_data = {"name": "The Hobbit"}

    # when
    with pytest.raises(TypeError):
        decode(book_data, Book)


def test_fails_to_encode_when_passed_invalid_type() -> None:
    # given
    class Book:
        name: str

    book = Book()

    # when
    with pytest.raises(TypeError):
        encode(book)
