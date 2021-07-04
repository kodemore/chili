import datetime

from chili.dataclasses import get_strategy_for


def test_hydrate_date() -> None:
    # given
    strategy = get_strategy_for(datetime.date)
    date = "2010-10-01"

    # when
    result = strategy.hydrate(date)

    # then
    assert isinstance(result, datetime.date)
    assert result.year == 2010
    assert result.month == 10
    assert result.day == 1


def test_extract_date() -> None:
    # given
    strategy = get_strategy_for(datetime.date)
    date = datetime.date(year=2010, month=10, day=1)

    # when
    result = strategy.extract(date)

    # then
    assert result == "2010-10-01"


def test_hydrate_time() -> None:
    # given
    strategy = get_strategy_for(datetime.time)
    time = "15:21:11"

    # when
    result = strategy.hydrate(time)

    # then
    assert isinstance(result, datetime.time)
    assert result.hour == 15
    assert result.minute == 21
    assert result.second == 11


def test_extract_time() -> None:
    # given
    strategy = get_strategy_for(datetime.time)
    time = datetime.time(hour=15, minute=21, second=11)

    # when
    result = strategy.extract(time)

    # then
    assert result == "15:21:11"


def test_hydrate_datetime() -> None:
    # given
    strategy = get_strategy_for(datetime.datetime)
    time = "2010-10-01T15:21:11"

    # when
    result = strategy.hydrate(time)

    # then
    assert isinstance(result, datetime.datetime)
    assert result.year == 2010
    assert result.month == 10
    assert result.day == 1
    assert result.hour == 15
    assert result.minute == 21
    assert result.second == 11


def test_extract_datetime() -> None:
    # given
    strategy = get_strategy_for(datetime.datetime)
    time = datetime.datetime(year=2010, month=10, day=1, hour=15, minute=21, second=11)

    # when
    result = strategy.extract(time)

    # then
    assert result == "2010-10-01T15:21:11"


def test_hydrate_timedelta() -> None:
    # given
    strategy = get_strategy_for(datetime.timedelta)
    time = "P1W3DT2H"

    # when
    result = strategy.hydrate(time)

    # then
    assert isinstance(result, datetime.timedelta)
    assert result.days == 10
    assert result.seconds == 7200


def test_extract_timedelta() -> None:
    # given
    strategy = get_strategy_for(datetime.timedelta)
    time = datetime.timedelta(days=10, seconds=7200)

    # when
    result = strategy.extract(time)

    # then
    assert result == "P1W3DT2H"
