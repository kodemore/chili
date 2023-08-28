from typing import List

from chili import Decoder, Mapper, decodable


def test_decodable_with_default_values() -> None:
    # given
    @decodable
    class Book:
        name: str
        author: str
        isbn: str = "1234567890"
        tags: List[str] = []

    book_data = {"name": "The Hobbit", "author": "J.R.R. Tolkien"}
    decoder = Decoder[Book]()

    # when
    result_1 = decoder.decode(book_data)

    result_1.tags.append("Fantasy")

    # then
    assert isinstance(result_1, Book)

    assert result_1.isbn == "1234567890"
    assert result_1.tags == ["Fantasy"]


def test_can_decode_with_mapper() -> None:
    # given
    mapper = Mapper({"_name": "name", "_author": "author"}, preserve_keys=True)

    @decodable(mapper=mapper)
    class Book:
        _name: str
        _author: str
        isbn: str
        tags: List[str] = []

    book_data = {
        "name": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "1234567890",
        "tags": ["Fantasy", "Adventure"],
    }
    decoder = Decoder[Book]()

    # when
    a_book = decoder.decode(book_data)

    # then
    assert isinstance(a_book, Book)
    assert a_book._name == "The Hobbit"
    assert a_book._author == "J.R.R. Tolkien"
    assert a_book.isbn == "1234567890"
    assert a_book.tags == ["Fantasy", "Adventure"]
