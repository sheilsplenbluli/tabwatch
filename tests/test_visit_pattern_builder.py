import pytest
from datetime import datetime, timezone
from app.models.domain_visit import DomainVisit
from app.services.visit_store import add_visit, _store
from app.services.visit_pattern_builder import build_visit_pattern, get_all_patterns_for_user


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(user_id, domain, hour=10, minutes=30.0):
    start = datetime(2024, 6, 10, hour, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 6, 10, hour, int(minutes), 0, tzinfo=timezone.utc)
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=end)
    add_visit(v)
    return v


def test_build_pattern_returns_none_for_unknown_domain():
    result = build_visit_pattern("u1", "nope.com")
    assert result is None


def test_build_pattern_correct_peak_hour():
    make_closed_visit("u1", "a.com", hour=9)
    make_closed_visit("u1", "a.com", hour=9)
    make_closed_visit("u1", "a.com", hour=14)
    pattern = build_visit_pattern("u1", "a.com")
    assert pattern is not None
    assert pattern.peak_hour == 9


def test_build_pattern_total_visits():
    make_closed_visit("u1", "b.com", hour=8)
    make_closed_visit("u1", "b.com", hour=20)
    pattern = build_visit_pattern("u1", "b.com")
    assert pattern.total_visits == 2


def test_build_pattern_avg_session_minutes():
    make_closed_visit("u1", "c.com", hour=10, minutes=20)
    make_closed_visit("u1", "c.com", hour=11, minutes=40)
    pattern = build_visit_pattern("u1", "c.com")
    assert pattern.avg_session_minutes == pytest.approx(30.0, abs=1.0)


def test_active_visits_excluded():
    v = DomainVisit(user_id="u1", domain="d.com",
                    start_time=datetime(2024, 6, 10, 10, 0, tzinfo=timezone.utc))
    add_visit(v)
    result = build_visit_pattern("u1", "d.com")
    assert result is None


def test_get_all_patterns_returns_multiple_domains():
    make_closed_visit("u2", "x.com", hour=7)
    make_closed_visit("u2", "y.com", hour=8)
    patterns = get_all_patterns_for_user("u2")
    domains = {p.domain for p in patterns}
    assert "x.com" in domains
    assert "y.com" in domains


def test_to_dict_contains_expected_keys():
    make_closed_visit("u3", "e.com", hour=12)
    pattern = build_visit_pattern("u3", "e.com")
    d = pattern.to_dict()
    assert "user_id" in d
    assert "domain" in d
    assert "hourly" in d
    assert "peak_hour" in d
    assert "avg_session_minutes" in d
    assert len(d["hourly"]) == 24
