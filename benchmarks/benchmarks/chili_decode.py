from typing import List, Optional
from chili import decodable, decode


@decodable
class Author:
    first_name: str
    last_name: str

@decodable
class Tag:
    name: str

@decodable
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

books = decode(raw_data, List[Book])
print(books)
