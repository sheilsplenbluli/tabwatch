"""Tracks daily visit streaks per user — how many consecutive days they've been active."""

from datetime import date, timedelta
from typing import Optional
from app.services.visit_store import get_visits_for_user


def get_active_dates(user_id: str) -> set[date]:
    """Return the set of calendar dates on which the user had at least one closed visit."""
    visits = get_visits_for_user(user_id)
    active = set()
    for v in visits:
        if v.end_time is not None:
            active.add(v.start_time.date())
    return active


def compute_current_streak(user_id: str, today: Optional[date] = None) -> int:
    """Return the number of consecutive days ending on today (or yesterday) with activity."""
    if today is None:
        today = date.today()

    active_dates = get_active_dates(user_id)
    if not active_dates:
        return 0

    # Allow streak to continue if the user was active today OR yesterday
    cursor = today if today in active_dates else today - timedelta(days=1)
    if cursor not in active_dates:
        return 0

    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return streak


def compute_longest_streak(user_id: str) -> int:
    """Return the longest consecutive-day streak the user has ever had."""
    active_dates = get_active_dates(user_id)
    if not active_dates:
        return 0

    sorted_dates = sorted(active_dates)
    longest = 1
    current = 1

    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1

    return longest


def get_streak_summary(user_id: str, today: Optional[date] = None) -> dict:
    """Return a dict with current and longest streak for the user."""
    return {
        "user_id": user_id,
        "current_streak": compute_current_streak(user_id, today),
        "longest_streak": compute_longest_streak(user_id),
    }
