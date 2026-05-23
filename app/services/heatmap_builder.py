from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Dict, List, Optional
from app.models.domain_visit import DomainVisit


def _date_key(dt: datetime) -> str:
    """Return ISO date string (YYYY-MM-DD) for a datetime."""
    return dt.date().isoformat()


def _hour_key(dt: datetime) -> int:
    """Return the hour (0-23) for a datetime."""
    return dt.hour


def build_daily_heatmap(
    visits: List[DomainVisit],
    domain: Optional[str] = None,
    days: int = 30,
) -> Dict[str, float]:
    """
    Return a mapping of date -> total minutes spent.
    Optionally filter by domain. Only considers closed visits
    within the last `days` days.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result: Dict[str, float] = {}

    for visit in visits:
        if visit.end_time is None:
            continue
        if visit.start_time < cutoff:
            continue
        if domain and visit.domain != domain:
            continue
        key = _date_key(visit.start_time)
        result[key] = result.get(key, 0.0) + (visit.duration_seconds or 0) / 60.0

    return result


def build_hourly_heatmap(
    visits: List[DomainVisit],
    domain: Optional[str] = None,
) -> Dict[int, float]:
    """
    Return a mapping of hour (0-23) -> total minutes spent across all time.
    Optionally filter by domain. Only considers closed visits.
    """
    result: Dict[int, float] = defaultdict(float)

    for visit in visits:
        if visit.end_time is None:
            continue
        if domain and visit.domain != domain:
            continue
        hour = _hour_key(visit.start_time)
        result[hour] += (visit.duration_seconds or 0) / 60.0

    return dict(result)


def get_heatmap_summary(
    visits: List[DomainVisit],
    domain: Optional[str] = None,
    days: int = 30,
) -> dict:
    """Return both daily and hourly heatmap data in a single dict."""
    daily = build_daily_heatmap(visits, domain=domain, days=days)
    hourly = build_hourly_heatmap(visits, domain=domain)
    peak_day = max(daily, key=daily.get, default=None)
    peak_hour = max(hourly, key=hourly.get, default=None)
    return {
        "daily": daily,
        "hourly": hourly,
        "peak_day": peak_day,
        "peak_hour": peak_hour,
    }
