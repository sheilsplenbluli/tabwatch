"""Aggregate notes and visit data for a domain into a summary report."""

from dataclasses import dataclass, field
from typing import List, Optional

from app.services.note_store import get_notes_for_domain
from app.services.visit_store import get_visits_for_user
from app.services.domain_insights import get_domain_insight


@dataclass
class DomainNotesSummary:
    user_id: str
    domain: str
    total_visits: int
    total_minutes: float
    note_count: int
    notes: List[dict] = field(default_factory=list)
    first_visited: Optional[str] = None
    last_visited: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "total_visits": self.total_visits,
            "total_minutes": round(self.total_minutes, 2),
            "note_count": self.note_count,
            "notes": self.notes,
            "first_visited": self.first_visited,
            "last_visited": self.last_visited,
        }


def build_domain_notes_summary(user_id: str, domain: str) -> Optional[DomainNotesSummary]:
    insight = get_domain_insight(user_id, domain)
    if insight is None:
        return None

    notes = get_notes_for_domain(user_id, domain)
    note_dicts = [n.to_dict() for n in notes]

    visits = [
        v for v in get_visits_for_user(user_id)
        if v.domain == domain and not v.is_active()
    ]

    first_visited = None
    last_visited = None
    if visits:
        sorted_visits = sorted(visits, key=lambda v: v.start_time)
        first_visited = sorted_visits[0].start_time.isoformat()
        last_visited = sorted_visits[-1].start_time.isoformat()

    return DomainNotesSummary(
        user_id=user_id,
        domain=domain,
        total_visits=insight.visit_count,
        total_minutes=insight.total_seconds / 60.0,
        note_count=len(notes),
        notes=note_dicts,
        first_visited=first_visited,
        last_visited=last_visited,
    )
