from typing import Optional
from app.models.site_rating import SiteRating

_store: dict[str, SiteRating] = {}


def _user_domain_key(user_id: str, domain: str) -> str:
    return f"{user_id}::{domain}"


def add_rating(rating: SiteRating) -> None:
    _store[rating.id] = rating


def get_rating(rating_id: str) -> Optional[SiteRating]:
    return _store.get(rating_id)


def get_rating_for_domain(user_id: str, domain: str) -> Optional[SiteRating]:
    for r in _store.values():
        if r.user_id == user_id and r.domain == domain:
            return r
    return None


def get_ratings_for_user(user_id: str) -> list[SiteRating]:
    return [r for r in _store.values() if r.user_id == user_id]


def update_rating(rating: SiteRating) -> None:
    _store[rating.id] = rating


def delete_rating(rating_id: str) -> bool:
    if rating_id in _store:
        del _store[rating_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()


def rating_count() -> int:
    return len(_store)
