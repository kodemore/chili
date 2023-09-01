from typing import List, Optional
from attrs import define
from cattr import structure


@define
class Author:
    first_name: str
    last_name: str


@define
class Tag:
    name: str


@define
class Book:
    name: str
    author: Author
    tags: List[Tag]
    isbn: Optional[str] = None


raw_data = [
    {
        "name": "The Hobbit",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    },
    {
        "name": "The Lord of the Rings",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    },
    {
        "name": "The Silmarillion",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    },
    {
        "name": "The Children of Húrin",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    },
    {
        "name": "The Fall of Gondolin",
        "author": {"first_name": "J.R.R.", "last_name": "Tolkien"},
        "tags": [{"name": "Fantasy"}, {"name": "Adventure"}],
    },
]

books = structure(raw_data, List[Book])
print(books)
