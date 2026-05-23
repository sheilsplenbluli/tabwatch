from typing import Dict, List, Optional, Tuple
from app.models.whitelist import WhitelistEntry

# store keyed by (user_id, domain)
_store: Dict[Tuple[str, str], WhitelistEntry] = {}


def add_entry(entry: WhitelistEntry) -> WhitelistEntry:
    key = (entry.user_id, entry.domain.lower())
    _store[key] = entry
    return entry


def get_entry(user_id: str, domain: str) -> Optional[WhitelistEntry]:
    return _store.get((user_id, domain.lower()))


def get_entries_for_user(user_id: str) -> List[WhitelistEntry]:
    return [e for (uid, _), e in _store.items() if uid == user_id]


def remove_entry(user_id: str, domain: str) -> bool:
    key = (user_id, domain.lower())
    if key in _store:
        del _store[key]
        return True
    return False


def is_whitelisted(user_id: str, domain: str) -> bool:
    return (user_id, domain.lower()) in _store


def clear_all() -> None:
    _store.clear()


def entry_count() -> int:
    return len(_store)
