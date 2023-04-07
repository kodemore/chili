from chili import TypeEncoder, encode, encodable, Encoder, TypeDecoder, decode
from chili.decoder import TypeDecoders
from chili.encoder import TypeEncoders


def test_can_define_custom_type_encoder() -> None:
    # given
    class ISBN(str):
        def __init__(self, value: str):
            self.value = value

    class ISBNEncoder(TypeEncoder):
        def encode(self, isbn: ISBN) -> str:
            return isbn.value

    # when
    result = encode(ISBN("1234567890"), encoders=TypeEncoders({ISBN: ISBNEncoder()}))

    # then
    assert result == "1234567890"


def test_can_define_custom_type_decoder() -> None:
    # given
    class ISBN(str):
        def __init__(self, value: str):
            self.value = value

    class ISBNDecoder(TypeDecoder):
        def decode(self, isbn: str) -> ISBN:
            return ISBN(isbn)

    # when
    result = decode("12345678", ISBN, decoders=TypeDecoders({ISBN: ISBNDecoder()}))

    # then
    assert isinstance(result, ISBN)



def test_can_define_custom_type_encoder_for_encoder() -> None:
    # given
    class ISBN(str):
        def __init__(self, value: str):
            self.value = value

    @encodable
    class Book:
        name: str
        isbn: ISBN

        def __init__(self, name: str, isbn: ISBN):
            self.name = name
            self.isbn = isbn


    class ISBNEncoder(TypeEncoder):
        def encode(self, isbn: ISBN) -> str:
            return isbn.value

    encoder = Encoder[Book]({ISBN: ISBNEncoder()})
    book = Book("The Hobbit", ISBN("1234567890"))

    # when
    result = encoder.encode(book)

    # then
    assert result == {"name": "The Hobbit", "isbn": "1234567890"}
