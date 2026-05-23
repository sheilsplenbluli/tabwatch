"""Compute day-over-day and week-over-week trends for a domain."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.services.visit_store import get_visits_for_user


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _minutes_in_window(visits, domain: str, start: datetime, end: datetime) -> float:
    total = 0.0
    for v in visits:
        if v.domain != domain:
            continue
        if v.end_time is None:
            continue
        if v.start_time >= start and v.start_time < end:
            total += (v.duration_seconds or 0) / 60.0
    return round(total, 2)


@dataclass
class DomainTrend:
    domain: str
    user_id: str
    current_period_minutes: float
    previous_period_minutes: float
    delta_minutes: float
    percent_change: Optional[float]  # None when previous == 0
    direction: str  # "up", "down", "flat"

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "user_id": self.user_id,
            "current_period_minutes": self.current_period_minutes,
            "previous_period_minutes": self.previous_period_minutes,
            "delta_minutes": self.delta_minutes,
            "percent_change": self.percent_change,
            "direction": self.direction,
        }


def compute_trend(
    user_id: str,
    domain: str,
    period_days: int = 7,
    reference_dt: Optional[datetime] = None,
) -> DomainTrend:
    """Compare the last *period_days* against the prior equal-length window."""
    now = reference_dt or _utcnow()
    current_start = now - timedelta(days=period_days)
    previous_start = current_start - timedelta(days=period_days)

    visits = get_visits_for_user(user_id)

    current_min = _minutes_in_window(visits, domain, current_start, now)
    previous_min = _minutes_in_window(visits, domain, previous_start, current_start)

    delta = round(current_min - previous_min, 2)

    if previous_min == 0:
        pct = None
    else:
        pct = round((delta / previous_min) * 100, 1)

    if delta > 0:
        direction = "up"
    elif delta < 0:
        direction = "down"
    else:
        direction = "flat"

    return DomainTrend(
        domain=domain,
        user_id=user_id,
        current_period_minutes=current_min,
        previous_period_minutes=previous_min,
        delta_minutes=delta,
        percent_change=pct,
        direction=direction,
    )
