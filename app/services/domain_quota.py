"""Domain quota service — daily visit count caps per user/domain."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.services.visit_store import get_visits_for_user

# { (user_id, domain): daily_limit }
_quota_store: dict[tuple[str, str], int] = {}


@dataclass
class QuotaStatus:
    user_id: str
    domain: str
    daily_limit: int
    visits_today: int
    exceeded: bool
    remaining: int

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "daily_limit": self.daily_limit,
            "visits_today": self.visits_today,
            "exceeded": self.exceeded,
            "remaining": self.remaining,
        }


def set_quota(user_id: str, domain: str, daily_limit: int) -> None:
    if daily_limit < 1:
        raise ValueError("daily_limit must be at least 1")
    _quota_store[(user_id, domain)] = daily_limit


def get_quota(user_id: str, domain: str) -> Optional[int]:
    return _quota_store.get((user_id, domain))


def delete_quota(user_id: str, domain: str) -> bool:
    key = (user_id, domain)
    if key in _quota_store:
        del _quota_store[key]
        return True
    return False


def get_quotas_for_user(user_id: str) -> dict[str, int]:
    return {
        domain: limit
        for (uid, domain), limit in _quota_store.items()
        if uid == user_id
    }


def _visits_today(user_id: str, domain: str) -> int:
    today = datetime.now(timezone.utc).date()
    visits = get_visits_for_user(user_id)
    return sum(
        1
        for v in visits
        if v.domain == domain and v.start_time.date() == today
    )


def check_quota(user_id: str, domain: str) -> Optional[QuotaStatus]:
    limit = get_quota(user_id, domain)
    if limit is None:
        return None
    today_count = _visits_today(user_id, domain)
    exceeded = today_count >= limit
    return QuotaStatus(
        user_id=user_id,
        domain=domain,
        daily_limit=limit,
        visits_today=today_count,
        exceeded=exceeded,
        remaining=max(0, limit - today_count),
    )


def clear_all_quotas() -> None:
    _quota_store.clear()
