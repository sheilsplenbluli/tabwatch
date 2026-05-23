from datetime import datetime, timezone
from typing import Optional
from app.services.visit_store import get_visits_for_user


def _closed_visits(user_id: str):
    return [v for v in get_visits_for_user(user_id) if not v.is_active()]


def _visits_in_range(visits, start: datetime, end: datetime):
    result = []
    for v in visits:
        if v.end_time and start <= v.end_time <= end:
            result.append(v)
    return result


def get_busiest_hour(user_id: str, start: datetime, end: datetime) -> Optional[int]:
    """Return the hour-of-day (0-23) with most visit time in range."""
    visits = _visits_in_range(_closed_visits(user_id), start, end)
    hour_totals: dict[int, float] = {}
    for v in visits:
        hour = v.start_time.hour
        hour_totals[hour] = hour_totals.get(hour, 0.0) + (v.duration_seconds or 0)
    if not hour_totals:
        return None
    return max(hour_totals, key=lambda h: hour_totals[h])


def get_busiest_day(user_id: str, start: datetime, end: datetime) -> Optional[str]:
    """Return ISO weekday name with most visit time in range."""
    visits = _visits_in_range(_closed_visits(user_id), start, end)
    day_totals: dict[str, float] = {}
    for v in visits:
        day = v.start_time.strftime("%A")
        day_totals[day] = day_totals.get(day, 0.0) + (v.duration_seconds or 0)
    if not day_totals:
        return None
    return max(day_totals, key=lambda d: day_totals[d])


def get_domain_visit_count(user_id: str, domain: str, start: datetime, end: datetime) -> int:
    """Return number of closed visits to a domain in range."""
    visits = _visits_in_range(_closed_visits(user_id), start, end)
    return sum(1 for v in visits if v.domain == domain)


def get_total_time_seconds(user_id: str, start: datetime, end: datetime) -> float:
    """Return total seconds spent browsing in range."""
    visits = _visits_in_range(_closed_visits(user_id), start, end)
    return sum(v.duration_seconds or 0 for v in visits)


def get_stats_summary(user_id: str, start: datetime, end: datetime) -> dict:
    total = get_total_time_seconds(user_id, start, end)
    return {
        "user_id": user_id,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "total_seconds": total,
        "total_minutes": round(total / 60, 2),
        "busiest_hour": get_busiest_hour(user_id, start, end),
        "busiest_day": get_busiest_day(user_id, start, end),
    }
