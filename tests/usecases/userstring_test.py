from collections import UserString

from chili import decode, encode


def test_can_encode_userstring() -> None:
    # given
    class ComplexString(UserString):
        pass

    string = ComplexString("Example String")

    # when
    result = encode(string)

    # then
    assert result == "Example String"


def test_can_decode_userstring() -> None:
    # given
    class ComplexString(UserString):
        pass

    string = "Example String"

    # when
    result = decode(string, ComplexString)

    # then
    assert result == ComplexString("Example String")
    assert isinstance(result, ComplexString)
    assert isinstance(result, UserString)
