from typing import Optional
from app.models.focus_goal import FocusGoal

_store: dict[str, FocusGoal] = {}


def add_goal(goal: FocusGoal) -> None:
    _store[goal.goal_id] = goal


def get_goal(goal_id: str) -> Optional[FocusGoal]:
    return _store.get(goal_id)


def get_goals_for_user(user_id: str) -> list[FocusGoal]:
    return [g for g in _store.values() if g.user_id == user_id]


def get_active_goals_for_user(user_id: str) -> list[FocusGoal]:
    return [g for g in _store.values() if g.user_id == user_id and g.is_active]


def update_goal(goal: FocusGoal) -> None:
    if goal.goal_id in _store:
        _store[goal.goal_id] = goal


def delete_goal(goal_id: str) -> bool:
    if goal_id in _store:
        del _store[goal_id]
        return True
    return False


def check_and_complete_goals(user_id: str, domain: str, minutes_today: float) -> list[FocusGoal]:
    """Mark goals as complete if the user has hit the target for a domain."""
    completed = []
    for goal in get_active_goals_for_user(user_id):
        if domain in goal.domains and minutes_today >= goal.target_minutes:
            goal.complete()
            completed.append(goal)
    return completed


def clear_all() -> None:
    _store.clear()
