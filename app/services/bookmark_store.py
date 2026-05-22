from typing import Optional
from app.models.bookmark import Bookmark

_store: dict[str, Bookmark] = {}


def add_bookmark(bookmark: Bookmark) -> None:
    _store[bookmark.bookmark_id] = bookmark


def get_bookmark(bookmark_id: str) -> Optional[Bookmark]:
    return _store.get(bookmark_id)


def get_bookmarks_for_user(user_id: str) -> list[Bookmark]:
    return [b for b in _store.values() if b.user_id == user_id]


def get_bookmarks_for_domain(user_id: str, domain: str) -> list[Bookmark]:
    return [
        b for b in _store.values()
        if b.user_id == user_id and b.domain == domain
    ]


def update_bookmark(bookmark: Bookmark) -> bool:
    if bookmark.bookmark_id not in _store:
        return False
    _store[bookmark.bookmark_id] = bookmark
    return True


def delete_bookmark(bookmark_id: str) -> bool:
    if bookmark_id not in _store:
        return False
    del _store[bookmark_id]
    return True


def bookmark_count() -> int:
    return len(_store)


def clear_all() -> None:
    _store.clear()
