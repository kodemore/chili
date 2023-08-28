from typing import List

from chili import Encoder, Mapper, encodable


def test_can_encode_encodable_with_undefined_field() -> None:
    # given
    @encodable
    class Book:
        name: str
        author: str
        isbn: str

        def __init__(self, name: str, author: str):
            self.name = name
            self.author = author

    book = Book("The Hobbit", "J.R.R. Tolkien")
    encoder = Encoder[Book]()

    # when
    result = encoder.encode(book)

    # then
    assert result == {"name": "The Hobbit", "author": "J.R.R. Tolkien"}


def test_can_encode_with_mapper() -> None:
    # given
    mapper = Mapper({"name": "_name", "author": "_author"}, preserve_keys=True)

    @encodable(mapper=mapper)
    class Book:
        _name: str
        _author: str
        isbn: str
        tags: List[str] = []

        def __init__(self, name: str, author: str, isbn: str, tags: List[str]):
            self._name = name
            self._author = author
            self.isbn = isbn
            self.tags = tags

    a_book = Book("The Hobbit", "J.R.R. Tolkien", "1234567890", ["Fantasy", "Adventure"])
    encoder = Encoder[Book]()

    # when
    result = encoder.encode(a_book)

    # then
    assert result == {
        "name": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "isbn": "1234567890",
        "tags": ["Fantasy", "Adventure"],
    }
