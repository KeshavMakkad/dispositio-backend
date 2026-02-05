from datetime import datetime, timezone


def get_current_datetime() -> datetime:
    """Get current datetime in UTC with timezone info."""
    return datetime.now(timezone.utc)


__all__ = ["get_current_datetime"]
