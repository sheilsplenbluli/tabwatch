"""Tests for domain_first_seen service."""

from datetime import datetime, timezone, timedelta

import pytest

from app.services import visit_store
from app.services.domain_first_seen import get_first_seen, get_all_first_seen
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    visit_store._store.clear()
    visit_store._user_index.clear()
    yield
    visit_store._store.clear()
    visit_store._user_index.clear()


def make_closed_visit(user_id: str, domain: str, start: datetime, duration: float = 60.0) -> DomainVisit:
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    end = start + timedelta(seconds=duration)
    v.close(end_time=end)
    visit_store.add_visit(v)
    return v


def test_get_first_seen_unknown_domain_returns_none():
    result = get_first_seen("user1", "example.com")
    assert result is None


def test_get_first_seen_returns_earliest_visit():
    now = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    make_closed_visit("user1", "example.com", now + timedelta(hours=2))
    make_closed_visit("user1", "example.com", now)
    make_closed_visit("user1", "example.com", now + timedelta(hours=5))

    result = get_first_seen("user1", "example.com")
    assert result is not None
    assert result.first_seen == now
    assert result.domain == "example.com"
    assert result.visit_count == 3


def test_get_first_seen_isolates_by_user():
    now = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    make_closed_visit("user1", "example.com", now)
    make_closed_visit("user2", "example.com", now + timedelta(days=1))

    r1 = get_first_seen("user1", "example.com")
    r2 = get_first_seen("user2", "example.com")
    assert r1.first_seen == now
    assert r2.first_seen == now + timedelta(days=1)


def test_get_first_seen_to_dict_contains_keys():
    now = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    make_closed_visit("user1", "news.ycombinator.com", now)
    result = get_first_seen("user1", "news.ycombinator.com")
    d = result.to_dict()
    assert "user_id" in d
    assert "domain" in d
    assert "first_seen" in d
    assert "visit_count" in d


def test_get_all_first_seen_returns_sorted_by_first_seen():
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    make_closed_visit("user1", "beta.com", t0 + timedelta(days=2))
    make_closed_visit("user1", "alpha.com", t0)
    make_closed_visit("user1", "gamma.com", t0 + timedelta(days=1))

    results = get_all_first_seen("user1")
    domains = [r.domain for r in results]
    assert domains == ["alpha.com", "gamma.com", "beta.com"]


def test_get_all_first_seen_empty_user_returns_empty():
    results = get_all_first_seen("nobody")
    assert results == []


def test_get_all_first_seen_visit_count_per_domain():
    t0 = datetime(2024, 3, 1, tzinfo=timezone.utc)
    make_closed_visit("user1", "a.com", t0)
    make_closed_visit("user1", "a.com", t0 + timedelta(hours=1))
    make_closed_visit("user1", "b.com", t0 + timedelta(hours=2))

    results = get_all_first_seen("user1")
    by_domain = {r.domain: r for r in results}
    assert by_domain["a.com"].visit_count == 2
    assert by_domain["b.com"].visit_count == 1
