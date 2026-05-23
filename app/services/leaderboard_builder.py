from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from app.services.visit_store import get_visits_for_user


@dataclass
class LeaderboardEntry:
    domain: str
    total_minutes: float
    visit_count: int

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "total_minutes": round(self.total_minutes, 2),
            "visit_count": self.visit_count,
        }


def _closed_visits_in_range(
    user_id: str,
    start: datetime,
    end: datetime,
):
    visits = get_visits_for_user(user_id)
    result = []
    for v in visits:
        if v.end_time is None:
            continue
        if v.start_time >= start and v.start_time < end:
            result.append(v)
    return result


def build_leaderboard(
    user_id: str,
    start: datetime,
    end: datetime,
    limit: int = 10,
) -> List[LeaderboardEntry]:
    visits = _closed_visits_in_range(user_id, start, end)

    totals: dict[str, float] = {}
    counts: dict[str, int] = {}

    for v in visits:
        domain = v.domain
        minutes = (v.duration_seconds or 0) / 60.0
        totals[domain] = totals.get(domain, 0.0) + minutes
        counts[domain] = counts.get(domain, 0) + 1

    entries = [
        LeaderboardEntry(domain=d, total_minutes=totals[d], visit_count=counts[d])
        for d in totals
    ]
    entries.sort(key=lambda e: e.total_minutes, reverse=True)
    return entries[:limit]
