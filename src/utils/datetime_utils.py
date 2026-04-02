from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def to_ist_naive(dt: datetime) -> datetime:
    """Normalize a datetime to IST and return it as timezone-naive for DB storage."""
    if dt.tzinfo is None:
        # Treat incoming naive datetimes as IST.
        return dt

    return dt.astimezone(IST).replace(tzinfo=None)


def to_ist_aware(dt: datetime) -> datetime:
    """Return an IST-aware datetime for API responses/comparisons."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST)

    return dt.astimezone(IST)


def get_current_datetime() -> datetime:
    """Get current datetime in IST (timezone-naive for DB comparisons)."""
    return datetime.now(IST).replace(tzinfo=None)


__all__ = ["IST", "get_current_datetime", "to_ist_aware", "to_ist_naive"]
