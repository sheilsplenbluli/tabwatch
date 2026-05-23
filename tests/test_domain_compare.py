"""Tests for domain_compare service."""

from datetime import datetime, timedelta

import pytest

from app.services.visit_store import add_visit, _store  # noqa: F401
from app.models.domain_visit import DomainVisit
from app.services.domain_compare import compare_domains


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(user_id, domain, start, duration_seconds):
    v = DomainVisit(
        visit_id=f"{user_id}-{domain}-{start.isoformat()}",
        user_id=user_id,
        domain=domain,
        start_time=start,
    )
    end = start + timedelta(seconds=duration_seconds)
    v.close(end)
    add_visit(v)
    return v


NOW = datetime(2024, 6, 10, 12, 0, 0)


def test_compare_returns_correct_minutes():
    make_closed_visit("u1", "github.com", NOW, 3600)   # 60 min
    make_closed_visit("u1", "reddit.com", NOW, 1800)   # 30 min

    result = compare_domains("u1", "github.com", "reddit.com")

    assert result.minutes_a == pytest.approx(60.0)
    assert result.minutes_b == pytest.approx(30.0)
    assert result.winner == "github.com"


def test_compare_visit_counts():
    for i in range(3):
        make_closed_visit("u1", "github.com", NOW + timedelta(hours=i), 600)
    make_closed_visit("u1", "reddit.com", NOW, 600)

    result = compare_domains("u1", "github.com", "reddit.com")

    assert result.visits_a == 3
    assert result.visits_b == 1


def test_compare_tied_winner_is_none():
    make_closed_visit("u1", "github.com", NOW, 600)
    make_closed_visit("u1", "reddit.com", NOW, 600)

    result = compare_domains("u1", "github.com", "reddit.com")
    assert result.winner is None


def test_compare_excludes_active_visits():
    make_closed_visit("u1", "github.com", NOW, 3600)
    # active visit for reddit — should not count
    active = DomainVisit(
        visit_id="active-1",
        user_id="u1",
        domain="reddit.com",
        start_time=NOW,
    )
    add_visit(active)

    result = compare_domains("u1", "github.com", "reddit.com")
    assert result.minutes_b == 0.0
    assert result.winner == "github.com"


def test_compare_respects_date_range():
    early = datetime(2024, 1, 1, 10, 0)
    late = datetime(2024, 6, 1, 10, 0)
    make_closed_visit("u1", "github.com", early, 3600)
    make_closed_visit("u1", "github.com", late, 600)
    make_closed_visit("u1", "reddit.com", late, 1200)

    cutoff = datetime(2024, 3, 1)
    result = compare_domains("u1", "github.com", "reddit.com", start=cutoff)

    # only the late github visit qualifies
    assert result.minutes_a == pytest.approx(10.0)
    assert result.minutes_b == pytest.approx(20.0)
    assert result.winner == "reddit.com"


def test_to_dict_shape():
    make_closed_visit("u1", "a.com", NOW, 120)
    make_closed_visit("u1", "b.com", NOW, 60)

    d = compare_domains("u1", "a.com", "b.com").to_dict()

    assert set(d.keys()) == {
        "user_id", "domain_a", "domain_b",
        "minutes_a", "minutes_b", "visits_a", "visits_b", "winner",
    }
    assert d["user_id"] == "u1"
