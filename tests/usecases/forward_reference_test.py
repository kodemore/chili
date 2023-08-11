from __future__ import annotations

from typing import List

import pytest

from chili import decode, serializable
from chili.error import SerialisationError


def test_can_decode_forward_reference():
    # given
    @serializable
    class Book:
        title: str
        author: Author
        tags: List[str]

    book_data = {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": {"name": "Douglas Adams"},
        "tags": ["sci-fi"],
    }

    # when
    book = decode(book_data, Book)

    # then
    assert isinstance(book, Book)
    assert isinstance(book.author, Author)


def test_fails_decode_forward_reference_with_inaccessible_locals() -> None:
    # given
    with pytest.raises(SerialisationError):

        @serializable
        class Book:
            title: str
            author: LocalAuthor
            tags: List[str]

    @serializable
    class LocalAuthor:
        name: str


@serializable
class Author:
    name: str
