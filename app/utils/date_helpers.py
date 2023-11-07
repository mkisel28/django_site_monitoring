from datetime import datetime, timedelta
from typing import Union


def apply_date_filter(query, date_filter: Union[str, int]) -> "QuerySet":
    """Applies date filter to the provided query."""
    if date_filter:
        today = datetime.today().date()
        if date_filter == "today":
            return query.filter(published_at__gte=today)
        elif date_filter == "week":
            return query.filter(published_at__gte=today - timedelta(days=7))
        elif date_filter == "month":
            return query.filter(published_at__gte=today - timedelta(days=30))
        elif type(date_filter) == int:
            return query.filter(published_at__gte=today - timedelta(days=date_filter))
    return query


