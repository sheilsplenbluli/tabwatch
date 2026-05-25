from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from app.services.visit_store import get_visits_for_user
from app.models.domain_visit import DomainVisit


@dataclass
class DomainSummaryEntry:
    domain: str
    total_visits: int
    total_minutes: float
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]
    avg_minutes_per_visit: float

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "total_visits": self.total_visits,
            "total_minutes": round(self.total_minutes, 2),
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "avg_minutes_per_visit": round(self.avg_minutes_per_visit, 2),
        }


def _closed_visits(user_id: str) -> List[DomainVisit]:
    return [v for v in get_visits_for_user(user_id) if not v.is_active()]


def build_domain_summary(user_id: str) -> List[DomainSummaryEntry]:
    visits = _closed_visits(user_id)
    aggregated: dict[str, dict] = {}

    for visit in visits:
        d = visit.domain
        if d not in aggregated:
            aggregated[d] = {
                "total_visits": 0,
                "total_minutes": 0.0,
                "first_seen": visit.start_time,
                "last_seen": visit.end_time,
            }
        agg = aggregated[d]
        agg["total_visits"] += 1
        agg["total_minutes"] += (visit.duration_seconds or 0) / 60.0
        if visit.start_time and (agg["first_seen"] is None or visit.start_time < agg["first_seen"]):
            agg["first_seen"] = visit.start_time
        if visit.end_time and (agg["last_seen"] is None or visit.end_time > agg["last_seen"]):
            agg["last_seen"] = visit.end_time

    results = []
    for domain, agg in aggregated.items():
        avg = agg["total_minutes"] / agg["total_visits"] if agg["total_visits"] > 0 else 0.0
        results.append(DomainSummaryEntry(
            domain=domain,
            total_visits=agg["total_visits"],
            total_minutes=agg["total_minutes"],
            first_seen=agg["first_seen"],
            last_seen=agg["last_seen"],
            avg_minutes_per_visit=avg,
        ))

    results.sort(key=lambda e: e.total_minutes, reverse=True)
    return results


def get_summary_for_domain(user_id: str, domain: str) -> Optional[DomainSummaryEntry]:
    summaries = build_domain_summary(user_id)
    for entry in summaries:
        if entry.domain == domain:
            return entry
    return None
