"""Ranks domains by visit frequency and total time for a user."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.services.visit_store import get_visits_for_user


@dataclass
class PopularityEntry:
    domain: str
    visit_count: int
    total_minutes: float
    last_visited: Optional[datetime]

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "visit_count": self.visit_count,
            "total_minutes": round(self.total_minutes, 2),
            "last_visited": self.last_visited.isoformat() if self.last_visited else None,
        }


def compute_popularity(
    user_id: str,
    limit: int = 10,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> List[PopularityEntry]:
    """Return domains ranked by visit count for the given user.

    Only closed visits are counted. Optional ``since``/``until`` bounds
    filter by visit start time.
    """
    visits = [
        v for v in get_visits_for_user(user_id)
        if not v.is_active() and v.duration_seconds is not None
    ]

    if since:
        visits = [v for v in visits if v.start_time >= since]
    if until:
        visits = [v for v in visits if v.start_time <= until]

    aggregated: dict[str, dict] = {}
    for v in visits:
        entry = aggregated.setdefault(
            v.domain,
            {"visit_count": 0, "total_minutes": 0.0, "last_visited": None},
        )
        entry["visit_count"] += 1
        entry["total_minutes"] += (v.duration_seconds or 0) / 60.0
        if entry["last_visited"] is None or v.start_time > entry["last_visited"]:
            entry["last_visited"] = v.start_time

    ranked = sorted(
        aggregated.items(),
        key=lambda kv: (kv[1]["visit_count"], kv[1]["total_minutes"]),
        reverse=True,
    )

    return [
        PopularityEntry(
            domain=domain,
            visit_count=data["visit_count"],
            total_minutes=data["total_minutes"],
            last_visited=data["last_visited"],
        )
        for domain, data in ranked[:limit]
    ]
