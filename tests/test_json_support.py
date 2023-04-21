from chili import (
    decodable,
    JsonDecoder,
    JsonEncoder,
    JsonSerializer,
    encodable,
    serializable,
)


def test_can_instantiate_json_decoder() -> None:
    # given
    @decodable
    class Example:
        ...

    # when
    instance = JsonDecoder[Example]()

    # then
    assert isinstance(instance, JsonDecoder)
    assert instance.__generic__ == Example


def test_can_instantiate_json_encoder() -> None:
    # given
    @encodable
    class Example:
        ...

    # when
    instance = JsonEncoder[Example]()

    # then
    assert isinstance(instance, JsonEncoder)
    assert instance.__generic__ == Example


def test_can_json_decode() -> None:
    # given
    @decodable
    class Author:
        first_name: str
        last_name: str

    @decodable
    class Book:
        name: str
        author: Author
        isbn: str

    book_json = '{"name": "The Hobbit", "author": {"first_name": "J.R.R.", "last_name": "Tolkien"}, "isbn": "1234567890"}'
    decoder = JsonDecoder[Book]()

    # when
    result = decoder.decode(book_json)

    # then
    assert isinstance(result, Book)
    assert result.name == "The Hobbit"
    assert result.isbn == "1234567890"
    assert isinstance(result.author, Author)
    assert result.author.first_name == "J.R.R."
    assert result.author.last_name == "Tolkien"


def test_can_json_encode() -> None:
    # given
    @encodable
    class Author:
        first_name: str
        last_name: str

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

    @encodable
    class Book:
        name: str
        author: Author
        isbn: str

        def __init__(self, name: str, author: Author, isbn: str):
            self.name = name
            self.author = author
            self.isbn = isbn

    book = Book("The Hobbit", Author("J.R.R.", "Tolkien"), "1234567890")
    encoder = JsonEncoder[Book]()

    # when
    result = encoder.encode(book)

    # then
    assert (
        result
        == '{"name": "The Hobbit", "author": {"first_name": "J.R.R.", "last_name": "Tolkien"}, "isbn": "1234567890"}'
    )


def test_fail_decode_invalid_json() -> None:
    # given
    @decodable
    class Example:
        ...

    decoder = JsonDecoder[Example]()

    # when
    try:
        decoder.decode("invalid json")
        assert False
    except ValueError:
        pass


def test_can_json_serialise() -> None:
    # given
    @serializable
    class Author:
        first_name: str
        last_name: str

        def __init__(self, first_name: str, last_name: str):
            self.first_name = first_name
            self.last_name = last_name

    @serializable
    class Book:
        name: str
        author: Author

        def __init__(self, name: str, author: Author):
            self.name = name
            self.author = author

    book_json = '{"name": "The Hobbit", "author": {"first_name": "J.R.R.", "last_name": "Tolkien"}}'
    serializer = JsonSerializer[Book]()
    book_instance = Book("The Hobbit", Author("J.R.R.", "Tolkien"))

    # when
    result = serializer.encode(book_instance)

    assert result == book_json

    result = serializer.decode(book_json)

    assert isinstance(result, Book)
