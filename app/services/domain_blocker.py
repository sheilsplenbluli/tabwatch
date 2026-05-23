"""Persistent domain block list per user (distinct from focus mode's temporary blocks)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class BlockedDomain:
    user_id: str
    domain: str
    reason: Optional[str] = None
    blocked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "reason": self.reason,
            "blocked_at": self.blocked_at.isoformat(),
        }


# In-memory store keyed by (user_id, domain)
_store: Dict[tuple, BlockedDomain] = {}


def block_domain(user_id: str, domain: str, reason: Optional[str] = None) -> BlockedDomain:
    key = (user_id, domain)
    entry = BlockedDomain(user_id=user_id, domain=domain, reason=reason)
    _store[key] = entry
    return entry


def unblock_domain(user_id: str, domain: str) -> bool:
    key = (user_id, domain)
    if key in _store:
        del _store[key]
        return True
    return False


def is_blocked(user_id: str, domain: str) -> bool:
    return (user_id, domain) in _store


def get_blocked_domains(user_id: str) -> List[BlockedDomain]:
    return [v for (uid, _), v in _store.items() if uid == user_id]


def clear_all() -> None:
    _store.clear()
