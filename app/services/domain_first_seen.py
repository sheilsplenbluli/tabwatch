"""Tracks the first time a domain was visited by a user."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.services.visit_store import get_visits_for_user


@dataclass
class DomainFirstSeen:
    user_id: str
    domain: str
    first_seen: datetime
    visit_count: int

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "first_seen": self.first_seen.isoformat(),
            "visit_count": self.visit_count,
        }


def get_first_seen(user_id: str, domain: str) -> Optional[DomainFirstSeen]:
    """Return first-seen info for a specific domain, or None if never visited."""
    visits = get_visits_for_user(user_id)
    domain_visits = [
        v for v in visits
        if v.domain == domain and v.start_time is not None
    ]
    if not domain_visits:
        return None

    earliest = min(domain_visits, key=lambda v: v.start_time)
    return DomainFirstSeen(
        user_id=user_id,
        domain=domain,
        first_seen=earliest.start_time,
        visit_count=len(domain_visits),
    )


def get_all_first_seen(user_id: str) -> list[DomainFirstSeen]:
    """Return first-seen info for every domain visited by the user."""
    visits = get_visits_for_user(user_id)
    domain_map: dict[str, list] = {}
    for v in visits:
        if v.start_time is not None:
            domain_map.setdefault(v.domain, []).append(v)

    results = []
    for domain, dvs in domain_map.items():
        earliest = min(dvs, key=lambda v: v.start_time)
        results.append(DomainFirstSeen(
            user_id=user_id,
            domain=domain,
            first_seen=earliest.start_time,
            visit_count=len(dvs),
        ))

    results.sort(key=lambda r: r.first_seen)
    return results
