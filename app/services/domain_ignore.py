from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

# In-memory store: {user_id: {entry_id: IgnoredDomain}}
_store: dict[str, dict[str, "IgnoredDomain"]] = {}


@dataclass
class IgnoredDomain:
    user_id: str
    domain: str
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
        }


def add_ignored(user_id: str, domain: str, reason: Optional[str] = None) -> IgnoredDomain:
    """Add a domain to the ignore list for a user. No-op if already present."""
    user_store = _store.setdefault(user_id, {})
    for entry in user_store.values():
        if entry.domain == domain:
            return entry
    entry = IgnoredDomain(user_id=user_id, domain=domain, reason=reason)
    user_store[entry.entry_id] = entry
    return entry


def remove_ignored(user_id: str, domain: str) -> bool:
    """Remove a domain from the ignore list. Returns True if removed."""
    user_store = _store.get(user_id, {})
    to_delete = [eid for eid, e in user_store.items() if e.domain == domain]
    for eid in to_delete:
        del user_store[eid]
    return len(to_delete) > 0


def is_ignored(user_id: str, domain: str) -> bool:
    return any(e.domain == domain for e in _store.get(user_id, {}).values())


def get_ignored_for_user(user_id: str) -> list[IgnoredDomain]:
    return list(_store.get(user_id, {}).values())


def clear_all() -> None:
    _store.clear()
