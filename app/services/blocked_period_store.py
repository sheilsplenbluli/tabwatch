from typing import Optional
from app.models.blocked_period import BlockedPeriod

_store: dict[str, BlockedPeriod] = {}


def add_period(period: BlockedPeriod) -> BlockedPeriod:
    _store[period.id] = period
    return period


def get_period(period_id: str) -> Optional[BlockedPeriod]:
    return _store.get(period_id)


def get_periods_for_user(user_id: str) -> list[BlockedPeriod]:
    return [p for p in _store.values() if p.user_id == user_id]


def update_period(period_id: str, updates: dict) -> Optional[BlockedPeriod]:
    period = _store.get(period_id)
    if period is None:
        return None
    for key, value in updates.items():
        if hasattr(period, key):
            setattr(period, key, value)
    return period


def delete_period(period_id: str) -> bool:
    if period_id in _store:
        del _store[period_id]
        return True
    return False


def is_in_blocked_period(user_id: str) -> bool:
    from datetime import datetime
    now = datetime.utcnow()
    return any(p.is_active_now(now) for p in get_periods_for_user(user_id))


def clear_all() -> None:
    _store.clear()
