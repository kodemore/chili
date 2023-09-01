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

book_schema = BookSchema(many=True)

raw_data = book_schema.dump(books)
print(raw_data)
