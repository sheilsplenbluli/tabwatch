"""In-memory store for domain visits, shared across the app."""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.models.domain_visit import DomainVisit

# visit_id -> DomainVisit
_store: Dict[str, DomainVisit] = {}


def add_visit(visit: DomainVisit) -> None:
    """Persist a new visit."""
    _store[visit.visit_id] = visit


def get_visit(visit_id: str) -> Optional[DomainVisit]:
    """Return a visit by ID, or None if not found."""
    return _store.get(visit_id)


def close_visit(visit_id: str, end_time: Optional[datetime] = None) -> Optional[DomainVisit]:
    """Close an active visit. Returns the updated visit or None if not found."""
    visit = _store.get(visit_id)
    if visit is None:
        return None
    if visit.is_active():
        visit.close(end_time or datetime.now(timezone.utc))
    return visit


def get_visits_for_user(user_id: str) -> List[DomainVisit]:
    """Return all visits belonging to a given user."""
    return [v for v in _store.values() if v.user_id == user_id]


def get_all_visits() -> List[DomainVisit]:
    """Return every visit currently in the store."""
    return list(_store.values())


def remove_visit(visit_id: str) -> bool:
    """Remove a visit from the store. Returns True if it existed."""
    if visit_id in _store:
        del _store[visit_id]
        return True
    return False


def clear_all() -> None:
    """Wipe the store (useful in tests)."""
    _store.clear()


def visit_count() -> int:
    """Return total number of stored visits."""
    return len(_store)
