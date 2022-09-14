from datetime import date, datetime, time, timedelta, timezone

import pytest

from chili.iso_datetime import (
    parse_iso_date,
    parse_iso_datetime,
    parse_iso_duration,
    parse_iso_time,
    timedelta_to_iso_duration,
)


@pytest.mark.parametrize(
    "given,expected",
    [
        ("202010", time(hour=20, minute=20, second=10, microsecond=0)),
        ("202010.000001", time(hour=20, minute=20, second=10, microsecond=1)),
        ("20:20:10.000001", time(hour=20, minute=20, second=10, microsecond=1)),
        ("20:20:10.000001Z", time(hour=20, minute=20, second=10, microsecond=1, tzinfo=timezone.utc)),
        (
            "20:20:10.000001+02:00",
            time(hour=20, minute=20, second=10, microsecond=1, tzinfo=timezone(timedelta(hours=2))),
        ),
    ],
)
def test_parse_iso_time_string(given, expected) -> None:
    assert parse_iso_time(given) == expected


def test_parse_simple_duration_strings() -> None:
    one_week = parse_iso_duration("P1W")
    assert one_week == timedelta(weeks=1)

    one_day = parse_iso_duration("P1D")
    assert one_day == timedelta(days=1)

    one_hour = parse_iso_duration("PT1H")
    assert one_hour == timedelta(hours=1)

    one_minute = parse_iso_duration("PT1M")
    assert one_minute == timedelta(minutes=1)

    one_second = parse_iso_duration("PT1S")
    assert one_second == timedelta(seconds=1)

    one_second_as_float = parse_iso_duration("PT1.234S")
    assert one_second_as_float == timedelta(seconds=1, milliseconds=234)


def test_parse_complex_duration_strings() -> None:
    w1d8s3 = parse_iso_duration("P1W8DT3S")
    assert w1d8s3 == timedelta(weeks=1, days=8, seconds=3)

    h5m6s7 = parse_iso_duration("PT5H6M7S")
    assert h5m6s7 == timedelta(hours=5, minutes=6, seconds=7)

    d2h3m4 = parse_iso_duration("P2DT3H4M")
    assert d2h3m4 == timedelta(days=2, hours=3, minutes=4)


@pytest.mark.parametrize(
    "given,expected",
    [
        (timedelta(days=7), "P1W"),
        (timedelta(days=11), "P1W4D"),
        (timedelta(hours=25), "P1DT1H"),
        (timedelta(minutes=12980), "P1W2DT20M"),
        (timedelta(minutes=13040), "P1W2DT1H20M"),
        (timedelta(seconds=80), "PT1M20S"),
        (timedelta(seconds=-80), "-PT1M20S"),
        (timedelta(minutes=1, seconds=-80), "-PT20S"),
    ],
)
def test_parse_timedelta_to_iso_string(given: timedelta, expected: str) -> None:
    assert timedelta_to_iso_duration(given) == expected


@pytest.mark.parametrize(
    "given, expected",
    [
        (
            "20201010T202010",
            datetime(year=2020, month=10, day=10, hour=20, minute=20, second=10, microsecond=0),
        ),
        (
            "20201010T202010.000001",
            datetime(year=2020, month=10, day=10, hour=20, minute=20, second=10, microsecond=1),
        ),
        (
            "2020-10-10T20:20:10.000001",
            datetime(year=2020, month=10, day=10, hour=20, minute=20, second=10, microsecond=1),
        ),
        (
            "2020-10-10 20:20:10.000001",
            datetime(year=2020, month=10, day=10, hour=20, minute=20, second=10, microsecond=1),
        ),
        (
            "2020-10-10 20:20:10.000001Z",
            datetime(
                year=2020,
                month=10,
                day=10,
                hour=20,
                minute=20,
                second=10,
                microsecond=1,
                tzinfo=timezone.utc,
            ),
        ),
    ],
)
def test_parse_iso_datetime_string(given: str, expected: datetime) -> None:
    assert parse_iso_datetime(given) == expected


@pytest.mark.parametrize(
    "given, expected",
    [
        ("20201210", date(year=2020, month=12, day=10)),
        ("2020-12-10", date(year=2020, month=12, day=10)),
        ("2020-1210", date(year=2020, month=12, day=10)),
        ("202012-10", date(year=2020, month=12, day=10)),
    ],
)
def test_parse_iso_date_string(given: str, expected: date) -> None:
    assert parse_iso_date(given) == expected
