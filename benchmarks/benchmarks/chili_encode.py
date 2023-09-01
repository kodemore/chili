from dataclasses import dataclass
from typing import List, Optional

from chili import encodable, encode


@encodable
@dataclass
class Author:
    first_name: str
    last_name: str

@encodable
@dataclass
class Tag:
    name: str

@encodable
@dataclass
class Book:
    name: str
    author: Author
    tags: List[Tag]
    isbn: Optional[str] = None


books = [
    Book(
        name="The Hobbit",
        author=Author(first_name="J.R.R.", last_name="Tolkien"),
        tags=[Tag(name="Fantasy"), Tag(name="Adventure")],
    ),
    Book(
        name="The Lord of the Rings",
        author=Author(first_name="J.R.R.", last_name="Tolkien"),
        tags=[Tag(name="Fantasy"), Tag(name="Adventure")],
    ),
    Book(
        name="The Silmarillion",
        author=Author(first_name="J.R.R.", last_name="Tolkien"),
        tags=[Tag(name="Fantasy"), Tag(name="Adventure")],
        isbn="978-0261102736",
    ),
    Book(
        name="The Children of Húrin",
        author=Author(first_name="J.R.R.", last_name="Tolkien"),
        tags=[Tag(name="Fantasy"), Tag(name="Adventure")],
    ),
    Book(
        name="The Fall of Gondolin",
        author=Author(first_name="J.R.R.", last_name="Tolkien"),
        tags=[Tag(name="Fantasy"), Tag(name="Adventure")],
    ),
]

raw_data = encode(books, List[Book])
print(raw_data)
