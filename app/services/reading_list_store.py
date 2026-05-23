from typing import Optional
from app.models.reading_list import ReadingListEntry

_store: dict[str, ReadingListEntry] = {}


def add_entry(entry: ReadingListEntry) -> None:
    _store[entry.entry_id] = entry


def get_entry(entry_id: str) -> Optional[ReadingListEntry]:
    return _store.get(entry_id)


def get_entries_for_user(user_id: str, include_archived: bool = False) -> list[ReadingListEntry]:
    results = [e for e in _store.values() if e.user_id == user_id]
    if not include_archived:
        results = [e for e in results if not e.archived]
    return sorted(results, key=lambda e: e.added_at, reverse=True)


def get_entries_for_domain(user_id: str, domain: str) -> list[ReadingListEntry]:
    return [
        e for e in _store.values()
        if e.user_id == user_id and e.domain == domain and not e.archived
    ]


def update_entry(entry: ReadingListEntry) -> None:
    if entry.entry_id in _store:
        _store[entry.entry_id] = entry


def delete_entry(entry_id: str) -> bool:
    if entry_id in _store:
        del _store[entry_id]
        return True
    return False


def entry_count() -> int:
    return len(_store)


def clear_all() -> None:
    _store.clear()
