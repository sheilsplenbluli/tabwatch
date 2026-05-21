from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

from app.models.domain_visit import DomainVisit


@dataclass
class DomainSummary:
    domain: str
    total_seconds: float
    visit_count: int

    @property
    def total_minutes(self) -> float:
        return round(self.total_seconds / 60, 2)

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "total_seconds": self.total_seconds,
            "total_minutes": self.total_minutes,
            "visit_count": self.visit_count,
        }


@dataclass
class WeeklyDigest:
    user_id: str
    week_start: datetime
    week_end: datetime
    summaries: List[DomainSummary] = field(default_factory=list)

    @classmethod
    def from_visits(cls, user_id: str, visits: List[DomainVisit], week_start: datetime) -> "WeeklyDigest":
        week_end = week_start + timedelta(days=7)
        relevant = [
            v for v in visits
            if v.end_time and week_start <= v.start_time < week_end
        ]

        totals: Dict[str, float] = defaultdict(float)
        counts: Dict[str, int] = defaultdict(int)

        for visit in relevant:
            totals[visit.domain] += visit.duration_seconds or 0
            counts[visit.domain] += 1

        summaries = [
            DomainSummary(domain=d, total_seconds=totals[d], visit_count=counts[d])
            for d in sorted(totals, key=lambda x: totals[x], reverse=True)
        ]

        return cls(user_id=user_id, week_start=week_start, week_end=week_end, summaries=summaries)

    def top_domains(self, n: int = 5) -> List[DomainSummary]:
        return self.summaries[:n]

    def total_tracked_seconds(self) -> float:
        return sum(s.total_seconds for s in self.summaries)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "week_start": self.week_start.isoformat(),
            "week_end": self.week_end.isoformat(),
            "total_tracked_seconds": self.total_tracked_seconds(),
            "summaries": [s.to_dict() for s in self.summaries],
        }
