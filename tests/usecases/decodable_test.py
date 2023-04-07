from typing import List

from chili import decodable, Decoder


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
