"""Compare time-spent statistics between two domains for a given user."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.services.visit_store import get_visits_for_user


@dataclass
class DomainCompareResult:
    user_id: str
    domain_a: str
    domain_b: str
    minutes_a: float
    minutes_b: float
    visits_a: int
    visits_b: int
    winner: Optional[str]  # domain with more time, or None if tied

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain_a": self.domain_a,
            "domain_b": self.domain_b,
            "minutes_a": round(self.minutes_a, 2),
            "minutes_b": round(self.minutes_b, 2),
            "visits_a": self.visits_a,
            "visits_b": self.visits_b,
            "winner": self.winner,
        }


def _sum_minutes(visits) -> float:
    return sum((v.duration_seconds or 0) / 60.0 for v in visits)


def compare_domains(
    user_id: str,
    domain_a: str,
    domain_b: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> DomainCompareResult:
    """Return a side-by-side comparison of two domains for *user_id*.

    Only closed visits are counted.  Optionally filter by *start* / *end*.

    Raises:
        ValueError: If *domain_a* and *domain_b* are the same domain.
    """
    if domain_a == domain_b:
        raise ValueError(
            f"domain_a and domain_b must be different domains, got {domain_a!r} for both"
        )

    all_visits = get_visits_for_user(user_id)

    def _filter(domain: str):
        result = [
            v for v in all_visits
            if v.domain == domain and v.end_time is not None
        ]
        if start:
            result = [v for v in result if v.start_time >= start]
        if end:
            result = [v for v in result if v.start_time <= end]
        return result

    visits_a = _filter(domain_a)
    visits_b = _filter(domain_b)

    mins_a = _sum_minutes(visits_a)
    mins_b = _sum_minutes(visits_b)

    if mins_a > mins_b:
        winner = domain_a
    elif mins_b > mins_a:
        winner = domain_b
    else:
        winner = None

    return DomainCompareResult(
        user_id=user_id,
        domain_a=domain_a,
        domain_b=domain_b,
        minutes_a=mins_a,
        minutes_b=mins_b,
        visits_a=len(visits_a),
        visits_b=len(visits_b),
        winner=winner,
    )
