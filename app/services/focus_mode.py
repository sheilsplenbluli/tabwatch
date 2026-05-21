"""Focus mode service — temporarily block or flag domains for a user."""

from datetime import datetime, timedelta
from typing import Optional

# In-memory store: {user_id: {domain: unblock_at}}
_focus_sessions: dict[str, dict[str, datetime]] = {}


def start_focus(user_id: str, blocked_domains: list[str], duration_minutes: int) -> dict:
    """Start a focus session blocking given domains for duration_minutes."""
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive")
    if not blocked_domains:
        raise ValueError("blocked_domains must not be empty")

    unblock_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
    _focus_sessions.setdefault(user_id, {})
    for domain in blocked_domains:
        _focus_sessions[user_id][domain] = unblock_at

    return {
        "user_id": user_id,
        "blocked_domains": blocked_domains,
        "unblock_at": unblock_at.isoformat(),
        "duration_minutes": duration_minutes,
    }


def stop_focus(user_id: str, domain: Optional[str] = None) -> int:
    """Stop focus session for a user. If domain given, unblock only that domain.
    Returns number of domains unblocked."""
    if user_id not in _focus_sessions:
        return 0
    if domain:
        removed = 1 if domain in _focus_sessions[user_id] else 0
        _focus_sessions[user_id].pop(domain, None)
        return removed
    count = len(_focus_sessions[user_id])
    del _focus_sessions[user_id]
    return count


def is_blocked(user_id: str, domain: str) -> bool:
    """Return True if domain is currently blocked for user."""
    sessions = _focus_sessions.get(user_id, {})
    unblock_at = sessions.get(domain)
    if unblock_at is None:
        return False
    if datetime.utcnow() >= unblock_at:
        # Expired — clean up
        del _focus_sessions[user_id][domain]
        return False
    return True


def get_focus_status(user_id: str) -> dict:
    """Return all currently blocked domains and their unblock times."""
    sessions = _focus_sessions.get(user_id, {})
    now = datetime.utcnow()
    active = {
        domain: unblock_at.isoformat()
        for domain, unblock_at in sessions.items()
        if unblock_at > now
    }
    return {"user_id": user_id, "blocked": active}


def clear_all_focus_sessions() -> None:
    """Clear all sessions (used in tests)."""
    _focus_sessions.clear()
