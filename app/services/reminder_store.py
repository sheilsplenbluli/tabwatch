from typing import Optional
from app.models.reminder import Reminder

_store: dict[str, Reminder] = {}


def add_reminder(reminder: Reminder) -> None:
    _store[reminder.id] = reminder


def get_reminder(reminder_id: str) -> Optional[Reminder]:
    return _store.get(reminder_id)


def get_reminders_for_user(user_id: str) -> list[Reminder]:
    return [r for r in _store.values() if r.user_id == user_id]


def get_reminders_for_domain(user_id: str, domain: str) -> list[Reminder]:
    return [
        r for r in _store.values()
        if r.user_id == user_id and r.domain == domain
    ]


def delete_reminder(reminder_id: str) -> bool:
    if reminder_id in _store:
        del _store[reminder_id]
        return True
    return False


def get_pending_reminders() -> list[Reminder]:
    """Return all untriggered reminders across all users."""
    return [r for r in _store.values() if not r.triggered]


def clear_all() -> None:
    _store.clear()


def reminder_count() -> int:
    return len(_store)
