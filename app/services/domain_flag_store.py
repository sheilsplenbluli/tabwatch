from typing import Optional
from app.models.domain_flag import DomainFlag

_store: dict[str, DomainFlag] = {}


def add_flag(flag: DomainFlag) -> None:
    _store[flag.flag_id] = flag


def get_flag(flag_id: str) -> Optional[DomainFlag]:
    return _store.get(flag_id)


def get_flags_for_user(user_id: str) -> list[DomainFlag]:
    return [f for f in _store.values() if f.user_id == user_id]


def get_flags_for_domain(user_id: str, domain: str) -> list[DomainFlag]:
    return [
        f for f in _store.values()
        if f.user_id == user_id and f.domain == domain
    ]


def get_unresolved_flags_for_user(user_id: str) -> list[DomainFlag]:
    return [f for f in get_flags_for_user(user_id) if not f.resolved]


def resolve_flag(flag_id: str, notes: str = "") -> Optional[DomainFlag]:
    flag = _store.get(flag_id)
    if flag:
        flag.resolve(notes)
    return flag


def delete_flag(flag_id: str) -> bool:
    if flag_id in _store:
        del _store[flag_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()
