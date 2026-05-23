import pytest
from datetime import datetime
from app.models.badge import Badge


def make_badge(**kwargs) -> Badge:
    defaults = {
        "badge_id": "test_badge",
        "user_id": "u1",
        "name": "Test Badge",
        "description": "A test badge.",
        "icon": "🏅",
    }
    defaults.update(kwargs)
    return Badge(**defaults)


def test_badge_defaults():
    b = make_badge()
    assert b.earned_at is None
    assert b.seen is False
    assert not b.is_earned()


def test_earn_sets_earned_at():
    b = make_badge()
    before = datetime.utcnow()
    b.earn()
    assert b.is_earned()
    assert b.earned_at >= before


def test_earn_is_idempotent():
    b = make_badge()
    b.earn()
    first_earned = b.earned_at
    b.earn()
    assert b.earned_at == first_earned


def test_earn_with_explicit_time():
    b = make_badge()
    t = datetime(2024, 1, 15, 12, 0, 0)
    b.earn(at=t)
    assert b.earned_at == t


def test_mark_seen_flips_flag():
    b = make_badge()
    b.earn()
    assert not b.seen
    b.mark_seen()
    assert b.seen


def test_to_dict_unearnerd():
    b = make_badge()
    d = b.to_dict()
    assert d["earned_at"] is None
    assert d["seen"] is False
    assert d["badge_id"] == "test_badge"


def test_to_dict_earned():
    b = make_badge()
    b.earn()
    d = b.to_dict()
    assert d["earned_at"] is not None


def test_round_trip_from_dict():
    b = make_badge()
    b.earn()
    b.mark_seen()
    restored = Badge.from_dict(b.to_dict())
    assert restored.badge_id == b.badge_id
    assert restored.earned_at == b.earned_at
    assert restored.seen is True
