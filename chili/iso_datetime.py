import re
from datetime import date, datetime, time, timedelta, timezone

ISO_8601_DATETIME_REGEX = re.compile(
    r"^(\d{4})-?([0-1]\d)-?([0-3]\d)[t\s]?([0-2]\d:?[0-5]\d:?[0-5]\d|23:59:60|235960)(\.\d+)?(z|[+-]\d{2}:\d{2})?$",
    re.I,
)
ISO_8601_DATE_REGEX = re.compile(r"^(\d{4})-?([0-1]\d)-?([0-3]\d)$", re.I)
ISO_8601_TIME_REGEX = re.compile(
    r"^(?P<time>[0-2]\d:?[0-5]\d:?[0-5]\d|23:59:60|235960)(?P<microseconds>\.\d+)?(?P<tzpart>z|[+-]\d{2}:\d{2})?$",
    re.I,
)

ISO_8601_TIME_DURATION_REGEX = re.compile(
    r"^(?P<sign>-?)P(?=\d|T\d)(?:(?P<weeks>\d+)W)?(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?)?$",
    re.I,
)


def parse_iso_datetime(value: str) -> datetime:

    if not ISO_8601_DATETIME_REGEX.match(value):
        raise ValueError(f"passed value {value!r} is not valid ISO-8601 datetime.")

    date_parts = ISO_8601_DATETIME_REGEX.findall(value)[0]
    time_part = date_parts[3]
    if ":" in time_part:
        time_part = time_part.split(":")
    else:
        time_part = list(map("".join, zip(*[iter(time_part)] * 2)))

    if date_parts[5] and date_parts[5].lower() != "z":
        sign = 1 if date_parts[5][0] == "+" else -1
        hours, minutes = date_parts[5][1:].split(":")
        offset = timezone(timedelta(hours=int(hours) * sign, minutes=int(minutes) * sign))
    elif date_parts[5] and date_parts[5].lower() == "z":
        offset = timezone.utc
    else:
        offset = None  # type: ignore

    return datetime(
        year=int(date_parts[0]),
        month=int(date_parts[1]),
        day=int(date_parts[2]),
        hour=int(time_part[0]),
        minute=int(time_part[1]),
        second=int(time_part[2]),
        tzinfo=offset,
    )


def parse_iso_date(value: str) -> date:
    if not ISO_8601_DATE_REGEX.match(value):
        raise ValueError("Passed value is not valid ISO-8601 date.")

    date_parts = ISO_8601_DATE_REGEX.findall(value)[0]
    return date(year=int(date_parts[0]), month=int(date_parts[1]), day=int(date_parts[2]))


def parse_iso_duration(value: str) -> timedelta:
    """
    Parses duration string according to ISO 8601 and returns timedelta representation (it excludes year and month)
    http://www.datypic.com/sc/xsd/t-xsd_dayTimeDuration.html
    :param str value:
    :return dict:
    """
    if not ISO_8601_TIME_DURATION_REGEX.match(value):
        raise ValueError(f"Passed value {value} is not valid ISO-8601 duration.")

    duration = ISO_8601_TIME_DURATION_REGEX.fullmatch(value)
    sign = -1 if duration.group("sign") else 1  # type: ignore

    kwargs = {
        "weeks": int(duration.group("weeks")) * sign if duration.group("weeks") else 0,  # type: ignore
        "days": int(duration.group("days")) * sign if duration.group("days") else 0,  # type: ignore
        "hours": int(duration.group("hours")) * sign if duration.group("hours") else 0,  # type: ignore
        "minutes": int(duration.group("minutes")) * sign  # type: ignore
        if duration.group("minutes")  # type: ignore
        else 0,
        "seconds": float(duration.group("seconds")) * sign  # type: ignore
        if duration.group("seconds")  # type: ignore
        else 0,
    }

    return timedelta(**kwargs)  # type: ignore


def parse_iso_time(value: str) -> time:
    if not ISO_8601_TIME_REGEX.match(value):
        raise ValueError(f"Passed value {value} is not valid ISO-8601 time.")

    time_parts = ISO_8601_TIME_REGEX.fullmatch(value)
    hour_parts = time_parts.group("time")  # type: ignore
    if ":" in hour_parts:
        hour_parts = hour_parts.split(":")
    else:
        hour_parts = list(map("".join, zip(*[iter(hour_parts)] * 2)))

    microseconds = time_parts.group("microseconds")  # type: ignore
    if microseconds is not None:
        microseconds = int(microseconds[1:])
    else:
        microseconds = 0

    tz_part = time_parts.group("tzpart")  # type: ignore
    if tz_part and tz_part.lower() != "z":
        sign = 1 if tz_part[0] == "+" else -1
        hours, minutes = tz_part[1:].split(":")
        offset = timezone(timedelta(hours=int(hours) * sign, minutes=int(minutes) * sign))
    elif tz_part and tz_part.lower() == "z":
        offset = timezone.utc
    else:
        offset = None  # type: ignore

    return time(
        hour=int(hour_parts[0]),
        minute=int(hour_parts[1]),
        second=int(hour_parts[2]),
        microsecond=microseconds,
        tzinfo=offset,
    )


def timedelta_to_iso_duration(value: timedelta) -> str:
    seconds = value.total_seconds()
    sign = "-" if seconds < 0 else ""
    seconds = abs(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    weeks, days, hours, minutes = map(int, (weeks, days, hours, minutes))
    seconds = round(seconds, 6)

    iso_8601 = sign + "P"
    iso_8601_date = ""
    iso_8601_time = ""
    if weeks:
        iso_8601_date += f"{weeks}W"

    if days:
        iso_8601_date += f"{days}D"

    if hours:
        iso_8601_time += f"{hours}H"

    if minutes:
        iso_8601_time += f"{minutes}M"

    if seconds:
        if seconds.is_integer():
            iso_8601_time += f"{int(seconds)}S"
        else:
            iso_8601_time += f"{seconds}S"

    return f"{iso_8601}{iso_8601_date}" + (f"T{iso_8601_time}" if iso_8601_time else "")


__all__ = [
    "parse_iso_datetime",
    "parse_iso_date",
    "parse_iso_duration",
    "parse_iso_time",
    "timedelta_to_iso_duration",
]
