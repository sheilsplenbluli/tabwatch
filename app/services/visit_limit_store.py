from typing import Optional
from app.models.visit_limit import VisitLimit

_store: dict[str, VisitLimit] = {}


def _user_domain_key(user_id: str, domain: str) -> str:
    return f"{user_id}::{domain}"


def set_limit(limit: VisitLimit) -> VisitLimit:
    key = _user_domain_key(limit.user_id, limit.domain)
    _store[key] = limit
    return limit


def get_limit(user_id: str, domain: str) -> Optional[VisitLimit]:
    return _store.get(_user_domain_key(user_id, domain))


def get_limits_for_user(user_id: str) -> list[VisitLimit]:
    return [v for k, v in _store.items() if k.startswith(f"{user_id}::")]


def delete_limit(user_id: str, domain: str) -> bool:
    key = _user_domain_key(user_id, domain)
    if key in _store:
        del _store[key]
        return True
    return False


def clear_all() -> None:
    _store.clear()
