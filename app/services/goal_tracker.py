from datetime import datetime, timezone
from typing import Optional
from app.services.visit_store import get_visits_for_user

# In-memory goal store: {user_id: {domain: daily_limit_minutes}}
_goal_store: dict[str, dict[str, int]] = {}


def set_goal(user_id: str, domain: str, daily_limit_minutes: int) -> dict:
    """Set or update a daily time goal for a domain."""
    if daily_limit_minutes <= 0:
        raise ValueError("daily_limit_minutes must be positive")
    if user_id not in _goal_store:
        _goal_store[user_id] = {}
    _goal_store[user_id][domain] = daily_limit_minutes
    return {"user_id": user_id, "domain": domain, "daily_limit_minutes": daily_limit_minutes}


def get_goal(user_id: str, domain: str) -> Optional[dict]:
    """Retrieve a goal for a specific domain, or None if not set."""
    limit = _goal_store.get(user_id, {}).get(domain)
    if limit is None:
        return None
    return {"user_id": user_id, "domain": domain, "daily_limit_minutes": limit}


def get_goals_for_user(user_id: str) -> list[dict]:
    """Return all goals for a user."""
    return [
        {"user_id": user_id, "domain": domain, "daily_limit_minutes": limit}
        for domain, limit in _goal_store.get(user_id, {}).items()
    ]


def delete_goal(user_id: str, domain: str) -> bool:
    """Remove a goal. Returns True if it existed."""
    if domain in _goal_store.get(user_id, {}):
        del _goal_store[user_id][domain]
        return True
    return False


def check_goal_progress(user_id: str, domain: str) -> Optional[dict]:
    """Return progress toward today's goal for a domain."""
    goal = get_goal(user_id, domain)
    if goal is None:
        return None

    today = datetime.now(timezone.utc).date()
    visits = get_visits_for_user(user_id)
    minutes_today = 0.0
    for v in visits:
        if v.domain != domain or v.end_time is None:
            continue
        if v.end_time.date() == today or v.start_time.date() == today:
            minutes_today += (v.duration_seconds or 0) / 60.0

    limit = goal["daily_limit_minutes"]
    percent = round((minutes_today / limit) * 100, 1) if limit > 0 else 0.0
    return {
        "domain": domain,
        "daily_limit_minutes": limit,
        "minutes_today": round(minutes_today, 2),
        "percent_used": percent,
        "over_limit": minutes_today > limit,
    }


def clear_all_goals() -> None:
    """Clear all goals (used in tests)."""
    _goal_store.clear()
