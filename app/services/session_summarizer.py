"""Summarizes browsing sessions by grouping visits into contiguous time blocks."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.domain_visit import DomainVisit

SESSION_GAP_MINUTES = 30  # visits more than this apart start a new session


@dataclass
class SessionSummary:
    user_id: str
    start_time: datetime
    end_time: datetime
    domains: List[str] = field(default_factory=list)
    total_minutes: float = 0.0

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "domains": self.domains,
            "total_minutes": round(self.total_minutes, 2),
        }


def _closed_visits_sorted(visits: List[DomainVisit]) -> List[DomainVisit]:
    """Return only closed visits sorted by start time."""
    closed = [v for v in visits if not v.is_active()]
    return sorted(closed, key=lambda v: v.start_time)


def build_sessions(
    user_id: str,
    visits: List[DomainVisit],
    gap_minutes: int = SESSION_GAP_MINUTES,
) -> List[SessionSummary]:
    """Group visits into sessions based on time proximity."""
    sorted_visits = _closed_visits_sorted(visits)
    if not sorted_visits:
        return []

    gap = timedelta(minutes=gap_minutes)
    sessions: List[SessionSummary] = []
    current: Optional[SessionSummary] = None

    for visit in sorted_visits:
        if current is None or visit.start_time - current.end_time > gap:
            current = SessionSummary(
                user_id=user_id,
                start_time=visit.start_time,
                end_time=visit.end_time,
                domains=[visit.domain],
                total_minutes=visit.duration_seconds / 60.0,
            )
            sessions.append(current)
        else:
            if visit.domain not in current.domains:
                current.domains.append(visit.domain)
            if visit.end_time > current.end_time:
                current.end_time = visit.end_time
            current.total_minutes += visit.duration_seconds / 60.0

    return sessions


def longest_session(sessions: List[SessionSummary]) -> Optional[SessionSummary]:
    """Return the session with the most total minutes, or None if empty."""
    if not sessions:
        return None
    return max(sessions, key=lambda s: s.total_minutes)
