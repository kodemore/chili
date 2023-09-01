from marshmallow import Schema, fields, post_load


class AuthorSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()

    @post_load
    def make_author(self, data, **kwargs):
        return Author(**data)


class Author:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


class TagSchema(Schema):
    name = fields.Str()

    @post_load
    def make_tag(self, data, **kwargs):
        return Tag(**data)


class Tag:
    def __init__(self, name):
        self.name = name


class Book:
    def __init__(self, name, author, tags, isbn=None):
        self.name = name
        self.author = author
        self.tags = tags
        self.isbn = isbn


class BookSchema(Schema):
    name = fields.Str()
    author = fields.Nested(AuthorSchema)
    tags = fields.Nested(TagSchema, many=True)
    isbn = fields.Str()

    @post_load
    def make_book(self, data, **kwargs):
        return Book(**data)


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

book_schema = BookSchema(many=True)

books = book_schema.load(raw_data)
print(books)
