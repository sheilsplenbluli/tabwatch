"""Tests for domain revisit stats."""
import pytest
from datetime import datetime, timedelta

from app.services.domain_revisit import compute_revisit_stats, get_all_revisit_stats
from app.services.visit_store import add_visit, _store  # noqa: F401
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    from app.services import visit_store
    visit_store._store.clear()
    visit_store._visits_by_user.clear()
    yield
    visit_store._store.clear()
    visit_store._visits_by_user.clear()


def make_closed_visit(user_id: str, domain: str, start: datetime, duration_minutes: float) -> DomainVisit:
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=start + timedelta(minutes=duration_minutes))
    add_visit(v)
    return v


def test_compute_revisit_stats_single_visit():
    now = datetime.utcnow()
    make_closed_visit("u1", "example.com", now - timedelta(days=1), 10)
    stats = compute_revisit_stats("u1", "example.com")
    assert stats is not None
    assert stats.visit_count == 1
    assert stats.revisit_count == 0
    assert stats.avg_gap_minutes == 0.0


def test_compute_revisit_stats_multiple_visits():
    now = datetime.utcnow()
    base = now - timedelta(days=5)
    make_closed_visit("u1", "example.com", base, 5)
    make_closed_visit("u1", "example.com", base + timedelta(hours=2), 5)
    make_closed_visit("u1", "example.com", base + timedelta(hours=5), 5)
    stats = compute_revisit_stats("u1", "example.com")
    assert stats.visit_count == 3
    assert stats.revisit_count == 2
    # gaps are 120 min and 180 min -> avg 150
    assert abs(stats.avg_gap_minutes - 150.0) < 0.1


def test_compute_revisit_stats_unknown_domain_returns_none():
    stats = compute_revisit_stats("u1", "ghost.com")
    assert stats is None


def test_compute_revisit_stats_excludes_active_visits():
    now = datetime.utcnow()
    v = DomainVisit(user_id="u1", domain="active.com", start_time=now - timedelta(hours=1))
    add_visit(v)  # never closed
    stats = compute_revisit_stats("u1", "active.com")
    assert stats is None


def test_compute_revisit_stats_respects_window():
    now = datetime.utcnow()
    make_closed_visit("u1", "old.com", now - timedelta(days=60), 10)
    make_closed_visit("u1", "old.com", now - timedelta(days=2), 10)
    stats = compute_revisit_stats("u1", "old.com", window_days=30)
    # Only the recent visit falls in the 30-day window
    assert stats.visit_count == 1
    assert stats.revisit_count == 0


def test_get_all_revisit_stats_returns_all_domains():
    now = datetime.utcnow()
    make_closed_visit("u2", "a.com", now - timedelta(days=1), 5)
    make_closed_visit("u2", "a.com", now - timedelta(hours=12), 5)
    make_closed_visit("u2", "b.com", now - timedelta(hours=6), 5)
    results = get_all_revisit_stats("u2")
    domains = {r.domain for r in results}
    assert "a.com" in domains
    assert "b.com" in domains


def test_get_all_revisit_stats_sorted_by_revisit_count():
    now = datetime.utcnow()
    make_closed_visit("u3", "frequent.com", now - timedelta(days=3), 5)
    make_closed_visit("u3", "frequent.com", now - timedelta(days=2), 5)
    make_closed_visit("u3", "frequent.com", now - timedelta(days=1), 5)
    make_closed_visit("u3", "rare.com", now - timedelta(days=1), 5)
    results = get_all_revisit_stats("u3")
    assert results[0].domain == "frequent.com"


def test_to_dict_contains_expected_keys():
    now = datetime.utcnow()
    make_closed_visit("u4", "check.com", now - timedelta(days=1), 10)
    stats = compute_revisit_stats("u4", "check.com")
    d = stats.to_dict()
    assert set(d.keys()) == {"domain", "user_id", "visit_count", "revisit_count", "avg_gap_minutes", "last_visited_at"}
