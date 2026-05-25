import pytest
from datetime import datetime, timedelta

from app.services.domain_summary import build_domain_summary, get_summary_for_domain
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(user_id: str, domain: str, minutes: float, offset_days: int = 0) -> DomainVisit:
    start = datetime(2024, 6, 1, 10, 0, 0) - timedelta(days=offset_days)
    end = start + timedelta(minutes=minutes)
    v = DomainVisit(
        visit_id=f"{user_id}-{domain}-{offset_days}-{minutes}",
        user_id=user_id,
        domain=domain,
        start_time=start,
        end_time=end,
        duration_seconds=minutes * 60,
    )
    add_visit(v)
    return v


def test_build_domain_summary_aggregates_visits():
    make_closed_visit("u1", "example.com", 10)
    make_closed_visit("u1", "example.com", 20)
    summaries = build_domain_summary("u1")
    assert len(summaries) == 1
    entry = summaries[0]
    assert entry.domain == "example.com"
    assert entry.total_visits == 2
    assert abs(entry.total_minutes - 30.0) < 0.01


def test_build_domain_summary_multiple_domains():
    make_closed_visit("u1", "alpha.com", 5)
    make_closed_visit("u1", "beta.com", 15)
    summaries = build_domain_summary("u1")
    domains = [s.domain for s in summaries]
    assert "alpha.com" in domains
    assert "beta.com" in domains


def test_build_domain_summary_sorted_by_total_minutes():
    make_closed_visit("u1", "low.com", 2)
    make_closed_visit("u1", "high.com", 50)
    make_closed_visit("u1", "mid.com", 20)
    summaries = build_domain_summary("u1")
    assert summaries[0].domain == "high.com"
    assert summaries[-1].domain == "low.com"


def test_build_domain_summary_excludes_active_visits():
    make_closed_visit("u1", "example.com", 10)
    active = DomainVisit(
        visit_id="active-1",
        user_id="u1",
        domain="active.com",
        start_time=datetime.utcnow(),
    )
    add_visit(active)
    summaries = build_domain_summary("u1")
    domains = [s.domain for s in summaries]
    assert "active.com" not in domains


def test_build_domain_summary_isolates_by_user():
    make_closed_visit("u1", "shared.com", 10)
    make_closed_visit("u2", "shared.com", 99)
    summaries = build_domain_summary("u1")
    assert len(summaries) == 1
    assert abs(summaries[0].total_minutes - 10.0) < 0.01


def test_avg_minutes_per_visit_calculated_correctly():
    make_closed_visit("u1", "calc.com", 10)
    make_closed_visit("u1", "calc.com", 30)
    entry = get_summary_for_domain("u1", "calc.com")
    assert entry is not None
    assert abs(entry.avg_minutes_per_visit - 20.0) < 0.01


def test_get_summary_for_unknown_domain_returns_none():
    result = get_summary_for_domain("u1", "ghost.com")
    assert result is None


def test_empty_store_returns_empty_list():
    summaries = build_domain_summary("u1")
    assert summaries == []
