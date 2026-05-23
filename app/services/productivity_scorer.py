"""Compute a simple productivity score for a user based on their browsing habits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from app.models.domain_visit import DomainVisit
from app.services.visit_store import get_visits_for_user

# Domains considered "productive" by default
PRODUCTIVE_DOMAINS: set[str] = {
    "github.com",
    "stackoverflow.com",
    "docs.python.org",
    "developer.mozilla.org",
    "notion.so",
    "linear.app",
    "figma.com",
}

# Domains considered "distracting" by default
DISTRACTING_DOMAINS: set[str] = {
    "twitter.com",
    "x.com",
    "reddit.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
}


@dataclass
class ProductivityScore:
    user_id: str
    productive_minutes: float
    distracting_minutes: float
    neutral_minutes: float
    score: float  # 0.0 – 100.0

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "productive_minutes": round(self.productive_minutes, 2),
            "distracting_minutes": round(self.distracting_minutes, 2),
            "neutral_minutes": round(self.neutral_minutes, 2),
            "score": round(self.score, 2),
        }


def _closed_visits_in_range(
    visits: List[DomainVisit], start: datetime, end: datetime
) -> List[DomainVisit]:
    result = []
    for v in visits:
        if v.end_time is None:
            continue
        if start <= v.start_time <= end:
            result.append(v)
    return result


def compute_productivity_score(
    user_id: str,
    start: datetime,
    end: datetime,
    productive: set[str] | None = None,
    distracting: set[str] | None = None,
) -> ProductivityScore:
    productive = productive if productive is not None else PRODUCTIVE_DOMAINS
    distracting = distracting if distracting is not None else DISTRACTING_DOMAINS

    all_visits = get_visits_for_user(user_id)
    visits = _closed_visits_in_range(all_visits, start, end)

    prod_min = 0.0
    dist_min = 0.0
    neut_min = 0.0

    for v in visits:
        minutes = (v.duration_seconds or 0) / 60.0
        if v.domain in productive:
            prod_min += minutes
        elif v.domain in distracting:
            dist_min += minutes
        else:
            neut_min += minutes

    total = prod_min + dist_min + neut_min
    if total == 0:
        score = 50.0
    else:
        score = ((prod_min + 0.5 * neut_min) / total) * 100.0

    return ProductivityScore(
        user_id=user_id,
        productive_minutes=prod_min,
        distracting_minutes=dist_min,
        neutral_minutes=neut_min,
        score=score,
    )
