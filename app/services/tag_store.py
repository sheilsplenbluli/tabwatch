import uuid
from typing import Dict, List, Optional
from app.models.tag import Tag

_store: Dict[str, Tag] = {}


def create_tag(user_id: str, name: str, domains: List[str] = None, color: str = None) -> Tag:
    tag = Tag(
        tag_id=str(uuid.uuid4()),
        user_id=user_id,
        name=name,
        domains=domains or [],
        color=color,
    )
    _store[tag.tag_id] = tag
    return tag


def get_tag(tag_id: str) -> Optional[Tag]:
    return _store.get(tag_id)


def get_tags_for_user(user_id: str) -> List[Tag]:
    return [t for t in _store.values() if t.user_id == user_id]


def update_tag(tag_id: str, name: str = None, domains: List[str] = None, color: str = None) -> Optional[Tag]:
    tag = _store.get(tag_id)
    if tag is None:
        return None
    if name is not None:
        tag.name = name
    if domains is not None:
        tag.domains = domains
    if color is not None:
        tag.color = color
    return tag


def delete_tag(tag_id: str) -> bool:
    if tag_id in _store:
        del _store[tag_id]
        return True
    return False


def get_tags_for_domain(user_id: str, domain: str) -> List[Tag]:
    return [t for t in get_tags_for_user(user_id) if t.matches_domain(domain)]


def clear_all_tags() -> None:
    _store.clear()
