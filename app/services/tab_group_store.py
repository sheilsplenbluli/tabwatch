from typing import Dict, List, Optional
from app.models.tab_group import TabGroup

_store: Dict[str, TabGroup] = {}


def create_group(group: TabGroup) -> TabGroup:
    _store[group.group_id] = group
    return group


def get_group(group_id: str) -> Optional[TabGroup]:
    return _store.get(group_id)


def get_groups_for_user(user_id: str) -> List[TabGroup]:
    return [g for g in _store.values() if g.user_id == user_id]


def update_group(group: TabGroup) -> TabGroup:
    _store[group.group_id] = group
    return group


def delete_group(group_id: str) -> bool:
    if group_id in _store:
        del _store[group_id]
        return True
    return False


def get_group_for_domain(user_id: str, domain: str) -> Optional[TabGroup]:
    for group in _store.values():
        if group.user_id == user_id and group.matches_domain(domain):
            return group
    return None


def clear_all() -> None:
    _store.clear()
