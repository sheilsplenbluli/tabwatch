"""Tests for the in-memory visit store."""

import pytest
from datetime import datetime, timezone, timedelta
from app.models.domain_visit import DomainVisit
import app.services.visit_store as store


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


def make_visit(user_id="user1", domain="example.com") -> DomainVisit:
    return DomainVisit(
        visit_id=f"{user_id}-{domain}-{id(object())}",
        user_id=user_id,
        domain=domain,
        start_time=datetime.now(timezone.utc),
    )


def test_add_and_get_visit():
    v = make_visit()
    store.add_visit(v)
    assert store.get_visit(v.visit_id) is v


def test_get_visit_unknown_returns_none():
    assert store.get_visit("nonexistent") is None


def test_visit_count_tracks_additions():
    assert store.visit_count() == 0
    store.add_visit(make_visit())
    store.add_visit(make_visit())
    assert store.visit_count() == 2


def test_get_visits_for_user_filters_correctly():
    v1 = make_visit(user_id="alice")
    v2 = make_visit(user_id="alice")
    v3 = make_visit(user_id="bob")
    for v in (v1, v2, v3):
        store.add_visit(v)

    alice_visits = store.get_visits_for_user("alice")
    assert len(alice_visits) == 2
    assert all(v.user_id == "alice" for v in alice_visits)


def test_get_visits_for_unknown_user_returns_empty():
    store.add_visit(make_visit(user_id="alice"))
    assert store.get_visits_for_user("nobody") == []


def test_close_visit_sets_end_time():
    v = make_visit()
    store.add_visit(v)
    assert v.is_active()

    end = datetime.now(timezone.utc) + timedelta(minutes=5)
    result = store.close_visit(v.visit_id, end)

    assert result is v
    assert not v.is_active()
    assert v.end_time == end


def test_close_visit_unknown_returns_none():
    assert store.close_visit("ghost-id") is None


def test_close_visit_already_closed_is_idempotent():
    v = make_visit()
    store.add_visit(v)
    end = datetime.now(timezone.utc) + timedelta(minutes=3)
    store.close_visit(v.visit_id, end)
    original_end = v.end_time

    # closing again should not change end_time
    store.close_visit(v.visit_id, end + timedelta(minutes=10))
    assert v.end_time == original_end


def test_remove_visit():
    v = make_visit()
    store.add_visit(v)
    assert store.remove_visit(v.visit_id) is True
    assert store.get_visit(v.visit_id) is None


def test_remove_nonexistent_visit_returns_false():
    assert store.remove_visit("nope") is False


def test_get_all_visits():
    v1, v2 = make_visit(), make_visit()
    store.add_visit(v1)
    store.add_visit(v2)
    all_visits = store.get_all_visits()
    assert len(all_visits) == 2
