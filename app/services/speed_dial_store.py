from typing import Optional
from app.models.speed_dial import SpeedDial

_store: dict[str, SpeedDial] = {}


def add_entry(entry: SpeedDial) -> None:
    _store[entry.id] = entry


def get_entry(entry_id: str) -> Optional[SpeedDial]:
    return _store.get(entry_id)


def get_entries_for_user(user_id: str) -> list[SpeedDial]:
    results = [e for e in _store.values() if e.user_id == user_id]
    return sorted(results, key=lambda e: (not e.pinned, e.position))


def get_entry_for_domain(user_id: str, domain: str) -> Optional[SpeedDial]:
    for entry in _store.values():
        if entry.user_id == user_id and entry.domain == domain:
            return entry
    return None


def update_entry(entry: SpeedDial) -> None:
    if entry.id in _store:
        _store[entry.id] = entry


def delete_entry(entry_id: str) -> bool:
    if entry_id in _store:
        del _store[entry_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()


def entry_count() -> int:
    return len(_store)
