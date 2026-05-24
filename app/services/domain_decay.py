"""Compute engagement decay score for domains based on recency of visits."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.services.visit_store import get_visits_for_user
from app.models.domain_visit import DomainVisit

_HALF_LIFE_DAYS = 7.0  # score halves every 7 days


@dataclass
class DomainDecayScore:
    domain: str
    score: float  # higher = more recently / frequently visited
    last_visit: Optional[str]  # ISO string
    visit_count: int

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "score": round(self.score, 4),
            "last_visit": self.last_visit,
            "visit_count": self.visit_count,
        }


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _decay_weight(visit_end: datetime, now: datetime) -> float:
    """Exponential decay weight based on age of visit."""
    age_days = (now - visit_end).total_seconds() / 86400.0
    if age_days < 0:
        age_days = 0.0
    return 2 ** (-age_days / _HALF_LIFE_DAYS)


def compute_decay_scores(user_id: str, now: Optional[datetime] = None) -> List[DomainDecayScore]:
    """Return decay-weighted engagement scores for all domains visited by user."""
    if now is None:
        now = _utcnow()

    raw_visits: List[DomainVisit] = get_visits_for_user(user_id)
    closed = [v for v in raw_visits if not v.is_active()]

    domain_data: dict = {}
    for visit in closed:
        end_dt = datetime.fromisoformat(visit.end_time) if isinstance(visit.end_time, str) else visit.end_time
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        weight = _decay_weight(end_dt, now)
        d = visit.domain
        if d not in domain_data:
            domain_data[d] = {"score": 0.0, "last_visit": end_dt, "count": 0}
        domain_data[d]["score"] += weight
        domain_data[d]["count"] += 1
        if end_dt > domain_data[d]["last_visit"]:
            domain_data[d]["last_visit"] = end_dt

    results = [
        DomainDecayScore(
            domain=domain,
            score=data["score"],
            last_visit=data["last_visit"].isoformat(),
            visit_count=data["count"],
        )
        for domain, data in domain_data.items()
    ]
    results.sort(key=lambda x: x.score, reverse=True)
    return results


def get_decay_score_for_domain(user_id: str, domain: str, now: Optional[datetime] = None) -> Optional[DomainDecayScore]:
    scores = compute_decay_scores(user_id, now=now)
    return next((s for s in scores if s.domain == domain), None)
