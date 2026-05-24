"""Tests for domain_popularity service."""

from datetime import datetime, timedelta

import pytest

from app.models.domain_visit import DomainVisit
from app.services.visit_store import add_visit, _store  # noqa: PLC2701
from app.services.domain_popularity import compute_popularity, PopularityEntry


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


NOW = datetime(2024, 6, 1, 12, 0, 0)


def make_closed_visit(user_id: str, domain: str, start: datetime, minutes: float) -> DomainVisit:
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    end = start + timedelta(minutes=minutes)
    v.close(end)
    add_visit(v)
    return v


def test_returns_list_of_popularity_entries():
    make_closed_visit("u1", "example.com", NOW, 10)
    result = compute_popularity("u1")
    assert len(result) == 1
    assert isinstance(result[0], PopularityEntry)


def test_ranks_by_visit_count_descending():
    make_closed_visit("u1", "a.com", NOW, 5)
    make_closed_visit("u1", "b.com", NOW, 5)
    make_closed_visit("u1", "b.com", NOW + timedelta(hours=1), 5)
    result = compute_popularity("u1")
    assert result[0].domain == "b.com"
    assert result[0].visit_count == 2
    assert result[1].domain == "a.com"


def test_total_minutes_aggregated():
    make_closed_visit("u1", "news.com", NOW, 15)
    make_closed_visit("u1", "news.com", NOW + timedelta(hours=2), 30)
    result = compute_popularity("u1")
    assert result[0].total_minutes == pytest.approx(45.0)


def test_excludes_active_visits():
    v = DomainVisit(user_id="u1", domain="active.com", start_time=NOW)
    add_visit(v)  # never closed
    result = compute_popularity("u1")
    assert result == []


def test_isolates_by_user():
    make_closed_visit("u1", "only-u1.com", NOW, 10)
    make_closed_visit("u2", "only-u2.com", NOW, 10)
    assert all(e.domain == "only-u1.com" for e in compute_popularity("u1"))
    assert all(e.domain == "only-u2.com" for e in compute_popularity("u2"))


def test_limit_respected():
    for i in range(8):
        make_closed_visit("u1", f"site{i}.com", NOW + timedelta(hours=i), 5)
    result = compute_popularity("u1", limit=3)
    assert len(result) == 3


def test_since_filter_excludes_older_visits():
    make_closed_visit("u1", "old.com", NOW - timedelta(days=10), 20)
    make_closed_visit("u1", "new.com", NOW, 5)
    cutoff = NOW - timedelta(days=1)
    result = compute_popularity("u1", since=cutoff)
    assert len(result) == 1
    assert result[0].domain == "new.com"


def test_until_filter_excludes_future_visits():
    make_closed_visit("u1", "past.com", NOW, 5)
    make_closed_visit("u1", "future.com", NOW + timedelta(days=5), 5)
    cutoff = NOW + timedelta(days=1)
    result = compute_popularity("u1", until=cutoff)
    assert len(result) == 1
    assert result[0].domain == "past.com"


def test_to_dict_shape():
    make_closed_visit("u1", "dict.com", NOW, 7)
    d = compute_popularity("u1")[0].to_dict()
    assert set(d.keys()) == {"domain", "visit_count", "total_minutes", "last_visited"}
    assert d["domain"] == "dict.com"
    assert d["visit_count"] == 1
