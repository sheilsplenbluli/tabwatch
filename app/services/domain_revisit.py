"""Tracks how often a user returns to a domain within a time window."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from app.services.visit_store import get_visits_for_user
from app.models.domain_visit import DomainVisit


@dataclass
class RevisitStats:
    domain: str
    user_id: str
    visit_count: int
    revisit_count: int  # visits after the first
    avg_gap_minutes: float  # avg minutes between consecutive visits
    last_visited_at: Optional[str]

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "user_id": self.user_id,
            "visit_count": self.visit_count,
            "revisit_count": self.revisit_count,
            "avg_gap_minutes": round(self.avg_gap_minutes, 2),
            "last_visited_at": self.last_visited_at,
        }


def _closed_visits_for_domain(
    user_id: str, domain: str, since: Optional[datetime] = None
) -> List[DomainVisit]:
    visits = [
        v for v in get_visits_for_user(user_id)
        if v.domain == domain and not v.is_active()
    ]
    if since:
        visits = [v for v in visits if v.start_time >= since]
    visits.sort(key=lambda v: v.start_time)
    return visits


def compute_revisit_stats(
    user_id: str,
    domain: str,
    window_days: int = 30,
) -> Optional[RevisitStats]:
    since = datetime.utcnow() - timedelta(days=window_days)
    visits = _closed_visits_for_domain(user_id, domain, since=since)

    if not visits:
        return None

    visit_count = len(visits)
    revisit_count = max(0, visit_count - 1)

    gaps: List[float] = []
    for i in range(1, len(visits)):
        delta = visits[i].start_time - visits[i - 1].start_time
        gaps.append(delta.total_seconds() / 60.0)

    avg_gap = sum(gaps) / len(gaps) if gaps else 0.0
    last_visited_at = visits[-1].start_time.isoformat() if visits else None

    return RevisitStats(
        domain=domain,
        user_id=user_id,
        visit_count=visit_count,
        revisit_count=revisit_count,
        avg_gap_minutes=avg_gap,
        last_visited_at=last_visited_at,
    )


def get_all_revisit_stats(
    user_id: str,
    window_days: int = 30,
) -> List[RevisitStats]:
    visits = get_visits_for_user(user_id)
    domains = {v.domain for v in visits if not v.is_active()}
    results = []
    for domain in domains:
        stats = compute_revisit_stats(user_id, domain, window_days=window_days)
        if stats:
            results.append(stats)
    results.sort(key=lambda s: s.revisit_count, reverse=True)
    return results
