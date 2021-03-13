import datetime
from typing import Optional

def start_of_day(dt: Optional[datetime.datetime] = None) -> datetime.datetime:
    dt = dt if dt is not None else datetime.datetime.now()
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def datetime_from_datetime(dt: datetime.datetime, days: int = 0, seconds: float = 0, milliseconds: int = 0, minutes: int = 0, hours: int = 0, weeks: int = 0) -> datetime.datetime:
    return dt + datetime.timedelta(days=days, seconds=seconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)
