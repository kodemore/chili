from pathlib import PurePosixPath, PureWindowsPath, PurePath, PosixPath, Path

from chili import encode, decode


def test_can_encode_pure_posix_path() -> None:
    # given
    path = PurePosixPath("/home/user")

    # when
    result = encode(path)

    # then
    assert result == "/home/user"


def test_can_decode_pure_posix_path() -> None:
    # given
    path = "/home/user"

    # when
    result = decode(path, PurePosixPath)

    # then
    assert isinstance(result, PurePosixPath)


def test_can_encode_pure_windows_path() -> None:
    # given
    path = PureWindowsPath("C:\\Users\\user")

    # when
    result = encode(path)

    # then
    assert result == "C:\\Users\\user"


def test_can_decode_pure_windows_path() -> None:
    # given
    path = "C:\\Users\\user"

    # when
    result = decode(path, PureWindowsPath)

    # then
    assert isinstance(result, PureWindowsPath)

def test_can_decode_pure_path() -> None:
    # given
    path = "/home/user"

    # when
    result = decode(path, PurePath)

    # then
    assert isinstance(result, PurePath)


def test_can_encode_pure_path() -> None:
    # given
    path = PurePath("/home/user")

    # when
    result = encode(path)

    # then
    assert result == "/home/user"

def test_can_decode_posix_path() -> None:
    # given
    path = "/home/user"

    # when
    result = decode(path, PosixPath)

    # then
    assert isinstance(result, PosixPath)


def test_can_encode_posix_path() -> None:
    # given
    path = PosixPath("/home/user")

    # when
    result = encode(path)

    # then
    assert result == "/home/user"


def test_can_decode_path() -> None:
    # given
    path = "/home/user"

    # when
    result = decode(path, Path)

    # then
    assert isinstance(result, Path)

def test_can_encode_path() -> None:
    # given
    path = Path("/home/user")

    # when
    result = encode(path)

    # then
    assert result == "/home/user"
