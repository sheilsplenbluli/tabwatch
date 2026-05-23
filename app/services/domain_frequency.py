"""Compute visit frequency stats for domains (visits per day average)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.domain_visit import DomainVisit
from app.services.visit_store import get_visits_for_user


@dataclass
class DomainFrequency:
    domain: str
    total_visits: int
    days_with_visits: int
    avg_visits_per_day: float
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "total_visits": self.total_visits,
            "days_with_visits": self.days_with_visits,
            "avg_visits_per_day": round(self.avg_visits_per_day, 2),
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


def _closed_visits(user_id: str, since: datetime, until: datetime) -> List[DomainVisit]:
    return [
        v for v in get_visits_for_user(user_id)
        if v.end_time is not None
        and since <= v.start_time <= until
    ]


def compute_frequency(
    user_id: str,
    since: datetime,
    until: datetime,
) -> List[DomainFrequency]:
    visits = _closed_visits(user_id, since, until)
    if not visits:
        return []

    total_days = max((until - since).days, 1)

    domain_visits: dict[str, List[DomainVisit]] = {}
    for v in visits:
        domain_visits.setdefault(v.domain, []).append(v)

    results: List[DomainFrequency] = []
    for domain, dvs in domain_visits.items():
        unique_days = len({v.start_time.date() for v in dvs})
        starts = [v.start_time for v in dvs]
        results.append(
            DomainFrequency(
                domain=domain,
                total_visits=len(dvs),
                days_with_visits=unique_days,
                avg_visits_per_day=len(dvs) / total_days,
                first_seen=min(starts),
                last_seen=max(starts),
            )
        )

    results.sort(key=lambda r: r.avg_visits_per_day, reverse=True)
    return results


def get_frequency_for_domain(
    user_id: str,
    domain: str,
    since: datetime,
    until: datetime,
) -> Optional[DomainFrequency]:
    all_freq = compute_frequency(user_id, since, until)
    return next((f for f in all_freq if f.domain == domain), None)
