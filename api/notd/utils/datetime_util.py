import datetime
def datetime_from_timestamp(timestamp: int) -> datetime.datetime: 
    return datetime.datetime.utcfromtimestamp(timestamp)