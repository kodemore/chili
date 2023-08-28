from typing import List

from chili import Mapper, Serializer, serializable


def test_serializable_with_mappers() -> None:
    # given
    encode_mapper = Mapper({"_name": "name", "_author": "author"}, preserve_keys=True)
    decode_mapper = Mapper({"name": "_name", "author": "_author"}, preserve_keys=True)

    @serializable(in_mapper=decode_mapper, out_mapper=encode_mapper)
    class Book:
        name: str
        author: str
        isbn: str
        tags: List[str] = []

        def __init__(self, name: str, author: str, isbn: str, tags: List[str]):
            self.name = name
            self.author = author
            self.isbn = isbn
            self.tags = tags

    a_book = Book("The Hobbit", "J.R.R. Tolkien", "1234567890", ["Fantasy", "Adventure"])
    a_book_snapshot = {
        "_name": "The Hobbit",
        "_author": "J.R.R. Tolkien",
        "isbn": "1234567890",
        "tags": ["Fantasy", "Adventure"],
    }
    serializer = Serializer[Book]()

    # when
    encoded_book = serializer.encode(a_book)
    decoded_book = serializer.decode(a_book_snapshot)

    # then
    assert encoded_book == a_book_snapshot
    assert decoded_book.name == "The Hobbit"
    assert decoded_book.author == "J.R.R. Tolkien"
    assert decoded_book.isbn == "1234567890"
    assert decoded_book.tags == ["Fantasy", "Adventure"]
