from typing import Dict, Union

from chili import encode, decode


def test_encode_dict() -> None:
    # given
    book = {"name": "The Hobbit", "author": "J.R.R. Tolkien", "no_pages": 295}

    # when
    result = encode(book, Dict[str, Union[str, int]])

    # then
    assert result == {"name": "The Hobbit", "author": "J.R.R. Tolkien", "no_pages": 295}


def test_decode_dict() -> None:
    # given
    book = {"name": "The Hobbit", "author": "J.R.R. Tolkien", "no_pages": "295"}

    # when
    result = decode(book, Dict[str, Union[str, int]])

    # then
    assert result == {
        "name": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "no_pages": "295",
    }
