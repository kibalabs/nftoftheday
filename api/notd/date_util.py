import datetime
from typing import Iterator, Optional, Tuple
from core.util import date_util


def date_hour_from_datetime(dt: Optional[datetime.datetime] = None) -> datetime.datetime:
    dt = dt if dt is not None else datetime.datetime.utcnow()
    return dt.replace(minute=0, second=0, microsecond=0)


def generate_clock_hour_intervals(startDate: datetime.datetime, endDate: datetime.datetime) -> Iterator[Tuple[datetime.datetime, datetime.datetime]]:
    # NOTE(krishan711) this has the results that look like [startDate, hourA]...[hourN, hourM]...[hourY, endDate]
    startDateNextHour = date_util.datetime_from_datetime(dt=date_hour_from_datetime(dt=startDate), hours=1)
    if startDate < startDateNextHour:
        yield (startDate, startDateNextHour)
    for periodStartDate, periodEndDate in generate_datetime_intervals(startDate=startDateNextHour, endDate=endDate, seconds=(60 * 60)):
        yield periodStartDate, periodEndDate


def generate_hourly_intervals(startDate: datetime.datetime, endDate: datetime.datetime) -> Iterator[Tuple[datetime.datetime, datetime.datetime]]:
    # NOTE(krishan711) this has the results that look like [startDate, startDate + 1hr]...[startDate + N hrs, endDate]
    return generate_datetime_intervals(startDate=startDate, endDate=endDate, seconds=(60 * 60))


def generate_datetime_intervals(startDate: datetime.datetime, endDate: datetime.datetime, seconds: int) -> Iterator[Tuple[datetime.datetime, datetime.datetime]]:
    counter = 1
    while startDate <= endDate:
        nextMaxDate = min(startDate + datetime.timedelta(seconds=counter * seconds), endDate)
        yield startDate, nextMaxDate
        if nextMaxDate == endDate:
            break
        startDate = nextMaxDate
