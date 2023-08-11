from typing import List

from chili import Encoder, encodable


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
