from typing import Dict, List, Optional
from app.models.category import Category

_store: Dict[str, Category] = {}


def create_category(category: Category) -> Category:
    _store[category.category_id] = category
    return category


def get_category(category_id: str) -> Optional[Category]:
    return _store.get(category_id)


def get_categories_for_user(user_id: str) -> List[Category]:
    return [c for c in _store.values() if c.user_id == user_id]


def update_category(category: Category) -> Category:
    _store[category.category_id] = category
    return category


def delete_category(category_id: str) -> bool:
    if category_id in _store:
        del _store[category_id]
        return True
    return False


def get_category_for_domain(user_id: str, domain: str) -> Optional[Category]:
    for c in _store.values():
        if c.user_id == user_id and c.matches_domain(domain):
            return c
    return None


def clear_all() -> None:
    _store.clear()
