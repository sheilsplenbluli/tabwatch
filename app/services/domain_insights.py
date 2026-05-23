from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from app.services.visit_store import get_visits_for_user
from app.models.domain_visit import DomainVisit


@dataclass
class DomainInsight:
    domain: str
    total_visits: int
    total_minutes: float
    avg_session_minutes: float
    first_seen: Optional[str]
    last_seen: Optional[str]
    busiest_hour: Optional[int]

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "total_visits": self.total_visits,
            "total_minutes": round(self.total_minutes, 2),
            "avg_session_minutes": round(self.avg_session_minutes, 2),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "busiest_hour": self.busiest_hour,
        }


def _closed_visits_for_domain(
    visits: List[DomainVisit], domain: str
) -> List[DomainVisit]:
    return [
        v for v in visits
        if v.domain == domain and not v.is_active()
    ]


def get_domain_insight(user_id: str, domain: str) -> Optional[DomainInsight]:
    all_visits = get_visits_for_user(user_id)
    visits = _closed_visits_for_domain(all_visits, domain)

    if not visits:
        return None

    total_minutes = sum(v.duration_seconds / 60.0 for v in visits if v.duration_seconds)
    avg_minutes = total_minutes / len(visits) if visits else 0.0

    start_times = [v.start_time for v in visits if v.start_time]
    start_times_sorted = sorted(start_times)
    first_seen = start_times_sorted[0].isoformat() if start_times_sorted else None
    last_seen = start_times_sorted[-1].isoformat() if start_times_sorted else None

    hour_counts: dict[int, int] = {}
    for v in visits:
        if v.start_time:
            h = v.start_time.hour
            hour_counts[h] = hour_counts.get(h, 0) + 1
    busiest_hour = max(hour_counts, key=lambda h: hour_counts[h]) if hour_counts else None

    return DomainInsight(
        domain=domain,
        total_visits=len(visits),
        total_minutes=total_minutes,
        avg_session_minutes=avg_minutes,
        first_seen=first_seen,
        last_seen=last_seen,
        busiest_hour=busiest_hour,
    )


def get_all_domain_insights(user_id: str) -> List[DomainInsight]:
    all_visits = get_visits_for_user(user_id)
    domains = {v.domain for v in all_visits if not v.is_active()}
    insights = []
    for domain in domains:
        insight = get_domain_insight(user_id, domain)
        if insight:
            insights.append(insight)
    insights.sort(key=lambda i: i.total_minutes, reverse=True)
    return insights
