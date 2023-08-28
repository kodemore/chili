from uuid import UUID

from chili import decode, encode


def test_can_encode_uuid() -> None:
    # given
    uuid = UUID("00000000-0000-0000-0000-000000000000")

    # when
    result = encode(uuid)

    # then
    assert result == "00000000-0000-0000-0000-000000000000"


def test_can_decode_uuid() -> None:
    # given
    uuid = "00000000-0000-0000-0000-000000000000"

    # when
    result = decode(uuid, UUID)

    # then
    assert result == UUID("00000000-0000-0000-0000-000000000000")
    assert isinstance(result, UUID)
