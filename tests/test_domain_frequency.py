"""Tests for domain_frequency service."""

from datetime import datetime, timedelta

import pytest

from app.services.domain_frequency import compute_frequency, get_frequency_for_domain
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


NOW = datetime(2024, 6, 10, 12, 0, 0)
SINCE = NOW - timedelta(days=6)
UNTIL = NOW


def make_closed_visit(user_id: str, domain: str, start: datetime, minutes: int = 5) -> DomainVisit:
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=start + timedelta(minutes=minutes))
    add_visit(v)
    return v


def test_compute_frequency_returns_correct_totals():
    make_closed_visit("u1", "example.com", NOW - timedelta(days=1))
    make_closed_visit("u1", "example.com", NOW - timedelta(days=2))
    make_closed_visit("u1", "example.com", NOW - timedelta(days=2))

    results = compute_frequency("u1", SINCE, UNTIL)
    assert len(results) == 1
    r = results[0]
    assert r.domain == "example.com"
    assert r.total_visits == 3
    assert r.days_with_visits == 2


def test_compute_frequency_avg_visits_per_day():
    for i in range(1, 4):
        make_closed_visit("u1", "news.com", NOW - timedelta(days=i))

    results = compute_frequency("u1", SINCE, UNTIL)
    r = next(x for x in results if x.domain == "news.com")
    expected_avg = 3 / max((UNTIL - SINCE).days, 1)
    assert abs(r.avg_visits_per_day - expected_avg) < 0.01


def test_compute_frequency_excludes_active_visits():
    active = DomainVisit(user_id="u1", domain="active.com", start_time=NOW - timedelta(hours=1))
    add_visit(active)
    make_closed_visit("u1", "closed.com", NOW - timedelta(days=1))

    results = compute_frequency("u1", SINCE, UNTIL)
    domains = [r.domain for r in results]
    assert "active.com" not in domains
    assert "closed.com" in domains


def test_compute_frequency_excludes_out_of_range():
    make_closed_visit("u1", "old.com", NOW - timedelta(days=30))
    make_closed_visit("u1", "recent.com", NOW - timedelta(days=1))

    results = compute_frequency("u1", SINCE, UNTIL)
    domains = [r.domain for r in results]
    assert "old.com" not in domains
    assert "recent.com" in domains


def test_compute_frequency_sorted_by_avg_desc():
    make_closed_visit("u1", "rare.com", NOW - timedelta(days=5))
    for i in range(1, 4):
        make_closed_visit("u1", "frequent.com", NOW - timedelta(days=i))

    results = compute_frequency("u1", SINCE, UNTIL)
    assert results[0].domain == "frequent.com"


def test_compute_frequency_empty_returns_empty():
    results = compute_frequency("u1", SINCE, UNTIL)
    assert results == []


def test_get_frequency_for_domain_returns_correct():
    make_closed_visit("u1", "target.com", NOW - timedelta(days=1))
    make_closed_visit("u1", "other.com", NOW - timedelta(days=2))

    result = get_frequency_for_domain("u1", "target.com", SINCE, UNTIL)
    assert result is not None
    assert result.domain == "target.com"


def test_get_frequency_for_domain_unknown_returns_none():
    result = get_frequency_for_domain("u1", "ghost.com", SINCE, UNTIL)
    assert result is None
