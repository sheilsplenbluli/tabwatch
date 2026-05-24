from typing import Optional
from app.models.page_title import PageTitle

_store: dict[str, PageTitle] = {}


def _url_key(user_id: str, url: str) -> str:
    return f"{user_id}::{url}"


def upsert_title(user_id: str, domain: str, url: str, title: str) -> PageTitle:
    """Create or update a PageTitle entry for the given URL."""
    key = _url_key(user_id, url)
    if key in _store:
        entry = _store[key]
        entry.touch(title)
    else:
        entry = PageTitle(user_id=user_id, domain=domain, url=url, title=title)
        _store[key] = entry
    return entry


def get_title(user_id: str, url: str) -> Optional[PageTitle]:
    return _store.get(_url_key(user_id, url))


def get_titles_for_user(user_id: str) -> list[PageTitle]:
    return [e for e in _store.values() if e.user_id == user_id]


def get_titles_for_domain(user_id: str, domain: str) -> list[PageTitle]:
    return [
        e for e in _store.values()
        if e.user_id == user_id and e.domain == domain
    ]


def delete_title(user_id: str, url: str) -> bool:
    key = _url_key(user_id, url)
    if key in _store:
        del _store[key]
        return True
    return False


def clear_all() -> None:
    _store.clear()


def title_count() -> int:
    return len(_store)
