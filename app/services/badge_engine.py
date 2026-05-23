from typing import List
from datetime import datetime, timezone

from app.models.badge import Badge
from app.services.streak_tracker import get_streak_summary
from app.services.visit_store import get_visits_for_user

_badge_store: dict[str, dict[str, Badge]] = {}


BADGE_DEFINITIONS = [
    {"badge_id": "first_visit", "name": "First Step", "description": "Recorded your first domain visit.", "icon": "🐣"},
    {"badge_id": "streak_3", "name": "3-Day Streak", "description": "Browsed for 3 days in a row.", "icon": "🔥"},
    {"badge_id": "streak_7", "name": "Week Warrior", "description": "Browsed for 7 days in a row.", "icon": "⚡"},
    {"badge_id": "century", "name": "Century", "description": "Logged 100 domain visits.", "icon": "💯"},
]


def _get_or_init_badges(user_id: str) -> dict[str, Badge]:
    if user_id not in _badge_store:
        _badge_store[user_id] = {
            defn["badge_id"]: Badge(
                badge_id=defn["badge_id"],
                user_id=user_id,
                name=defn["name"],
                description=defn["description"],
                icon=defn["icon"],
            )
            for defn in BADGE_DEFINITIONS
        }
    return _badge_store[user_id]


def evaluate_badges(user_id: str) -> List[Badge]:
    """Check conditions and earn any newly qualifying badges. Returns newly earned badges."""
    badges = _get_or_init_badges(user_id)
    visits = get_visits_for_user(user_id)
    streak_summary = get_streak_summary(user_id)
    current_streak = streak_summary.get("current_streak", 0)
    newly_earned: List[Badge] = []

    def _earn(badge_id: str) -> None:
        b = badges[badge_id]
        if not b.is_earned():
            b.earn()
            newly_earned.append(b)

    if visits:
        _earn("first_visit")
    if current_streak >= 3:
        _earn("streak_3")
    if current_streak >= 7:
        _earn("streak_7")
    if len(visits) >= 100:
        _earn("century")

    return newly_earned


def get_badges_for_user(user_id: str) -> List[Badge]:
    return list(_get_or_init_badges(user_id).values())


def get_unseen_badges(user_id: str) -> List[Badge]:
    return [b for b in get_badges_for_user(user_id) if b.is_earned() and not b.seen]


def mark_badges_seen(user_id: str) -> None:
    for badge in get_badges_for_user(user_id):
        if badge.is_earned():
            badge.mark_seen()


def clear_all_badges() -> None:
    _badge_store.clear()
