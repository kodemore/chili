from collections import OrderedDict

from chili import encode, decode


def test_can_encode_ordered_dict() -> None:
    # given
    values = OrderedDict(a=1, b=2, c=3)

    # when
    result = encode(values, OrderedDict[str, int])

    # then
    assert result == [["a", 1], ["b", 2], ["c", 3]]


def test_can_decode_ordered_dict() -> None:
    # given
    values = [["a", 1], ["b", 2], ["c", 3]]

    # when
    result = decode(values, OrderedDict[str, int])

    # then
    assert result == OrderedDict(a=1, b=2, c=3)
