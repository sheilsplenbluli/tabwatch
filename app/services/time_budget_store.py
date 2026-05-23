from typing import Optional
from app.models.time_budget import TimeBudget

_store: dict[str, TimeBudget] = {}


def add_budget(budget: TimeBudget) -> None:
    _store[budget.budget_id] = budget


def get_budget(budget_id: str) -> Optional[TimeBudget]:
    return _store.get(budget_id)


def get_budgets_for_user(user_id: str) -> list[TimeBudget]:
    return [b for b in _store.values() if b.user_id == user_id]


def get_budget_for_domain(user_id: str, domain: str) -> Optional[TimeBudget]:
    for b in _store.values():
        if b.user_id == user_id and b.domain == domain:
            return b
    return None


def update_budget(budget: TimeBudget) -> None:
    _store[budget.budget_id] = budget


def delete_budget(budget_id: str) -> bool:
    if budget_id in _store:
        del _store[budget_id]
        return True
    return False


def clear_all() -> None:
    _store.clear()
