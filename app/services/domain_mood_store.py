from typing import Optional
from app.models.domain_mood import DomainMood

_store: dict[str, DomainMood] = {}


def _user_domain_key(user_id: str, domain: str) -> str:
    return f"{user_id}::{domain}"


def add_mood(mood: DomainMood) -> None:
    _store[mood.mood_id] = mood


def get_mood(mood_id: str) -> Optional[DomainMood]:
    return _store.get(mood_id)


def get_moods_for_user(user_id: str) -> list[DomainMood]:
    return [m for m in _store.values() if m.user_id == user_id]


def get_moods_for_domain(user_id: str, domain: str) -> list[DomainMood]:
    return [
        m for m in _store.values()
        if m.user_id == user_id and m.domain == domain
    ]


def update_mood(mood: DomainMood) -> None:
    if mood.mood_id in _store:
        _store[mood.mood_id] = mood


def delete_mood(mood_id: str) -> bool:
    if mood_id in _store:
        del _store[mood_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()
