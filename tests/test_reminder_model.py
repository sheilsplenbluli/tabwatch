import pytest
from datetime import datetime, timedelta
from app.models.reminder import Reminder


def make_reminder(**kwargs) -> Reminder:
    defaults = dict(
        user_id="u1",
        domain="example.com",
        message="Check your usage!",
        remind_at=datetime(2024, 6, 1, 9, 0, 0),
    )
    defaults.update(kwargs)
    return Reminder(**defaults)


def test_reminder_defaults():
    r = make_reminder()
    assert r.triggered is False
    assert r.triggered_at is None
    assert r.id is not None
    assert r.created_at is not None


def test_trigger_sets_flags():
    r = make_reminder()
    r.trigger()
    assert r.triggered is True
    assert r.triggered_at is not None


def test_trigger_is_idempotent():
    r = make_reminder()
    r.trigger()
    first_time = r.triggered_at
    r.trigger()
    assert r.triggered_at == first_time


def test_is_due_when_past_remind_at():
    past = datetime.utcnow() - timedelta(minutes=5)
    r = make_reminder(remind_at=past)
    assert r.is_due() is True


def test_is_not_due_when_future():
    future = datetime.utcnow() + timedelta(hours=1)
    r = make_reminder(remind_at=future)
    assert r.is_due() is False


def test_is_not_due_when_already_triggered():
    past = datetime.utcnow() - timedelta(minutes=5)
    r = make_reminder(remind_at=past)
    r.trigger()
    assert r.is_due() is False


def test_to_dict_and_from_dict_roundtrip():
    r = make_reminder()
    r.trigger()
    d = r.to_dict()
    restored = Reminder.from_dict(d)
    assert restored.id == r.id
    assert restored.domain == r.domain
    assert restored.triggered is True
    assert restored.triggered_at is not None
