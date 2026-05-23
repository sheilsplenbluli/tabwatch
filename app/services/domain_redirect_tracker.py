from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid

# In-memory store: redirect_id -> RedirectRecord
_store: dict[str, dict] = {}


@dataclass
class RedirectRecord:
    redirect_id: str
    user_id: str
    from_domain: str
    to_domain: str
    count: int = 0
    last_seen: Optional[str] = None

    def increment(self, timestamp: str) -> None:
        self.count += 1
        self.last_seen = timestamp

    def to_dict(self) -> dict:
        return {
            "redirect_id": self.redirect_id,
            "user_id": self.user_id,
            "from_domain": self.from_domain,
            "to_domain": self.to_domain,
            "count": self.count,
            "last_seen": self.last_seen,
        }


def _make_key(user_id: str, from_domain: str, to_domain: str) -> str:
    return f"{user_id}:{from_domain}->{to_domain}"


def record_redirect(user_id: str, from_domain: str, to_domain: str, timestamp: str) -> RedirectRecord:
    key = _make_key(user_id, from_domain, to_domain)
    existing = next((r for r in _store.values() if
                     r["user_id"] == user_id and
                     r["from_domain"] == from_domain and
                     r["to_domain"] == to_domain), None)
    if existing:
        rec = _record_from_dict(existing)
        rec.increment(timestamp)
        _store[rec.redirect_id] = rec.to_dict()
        return rec

    rid = str(uuid.uuid4())
    rec = RedirectRecord(
        redirect_id=rid,
        user_id=user_id,
        from_domain=from_domain,
        to_domain=to_domain,
        count=1,
        last_seen=timestamp,
    )
    _store[rid] = rec.to_dict()
    return rec


def get_redirects_for_user(user_id: str) -> list[RedirectRecord]:
    return [_record_from_dict(v) for v in _store.values() if v["user_id"] == user_id]


def get_redirect(redirect_id: str) -> Optional[RedirectRecord]:
    entry = _store.get(redirect_id)
    return _record_from_dict(entry) if entry else None


def delete_redirect(redirect_id: str) -> bool:
    if redirect_id in _store:
        del _store[redirect_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()


def _record_from_dict(d: dict) -> RedirectRecord:
    return RedirectRecord(
        redirect_id=d["redirect_id"],
        user_id=d["user_id"],
        from_domain=d["from_domain"],
        to_domain=d["to_domain"],
        count=d["count"],
        last_seen=d["last_seen"],
    )
