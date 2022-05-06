import datetime
from typing import Optional

from core.util import date_util


def date_hour_from_datetime(dt: Optional[datetime.datetime] = None) -> datetime.datetime:
    dt = dt if dt is not None else datetime.datetime.utcnow()
    return dt.replace(minute=0, second=0, microsecond=0)
