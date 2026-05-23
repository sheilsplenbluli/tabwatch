import pytest
from datetime import datetime, timezone, timedelta

from app.services.domain_insights import get_domain_insight, get_all_domain_insights
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(
    user_id: str,
    domain: str,
    start: datetime,
    duration_seconds: int = 300,
) -> DomainVisit:
    end = start + timedelta(seconds=duration_seconds)
    visit = DomainVisit(
        visit_id=f"{user_id}-{domain}-{start.isoformat()}",
        user_id=user_id,
        domain=domain,
        start_time=start,
        end_time=end,
        duration_seconds=duration_seconds,
    )
    add_visit(visit)
    return visit


BASE = datetime(2024, 6, 10, 9, 0, 0, tzinfo=timezone.utc)


def test_get_domain_insight_returns_correct_totals():
    make_closed_visit("u1", "example.com", BASE, 600)
    make_closed_visit("u1", "example.com", BASE + timedelta(hours=2), 300)

    insight = get_domain_insight("u1", "example.com")
    assert insight is not None
    assert insight.domain == "example.com"
    assert insight.total_visits == 2
    assert abs(insight.total_minutes - 15.0) < 0.01
    assert abs(insight.avg_session_minutes - 7.5) < 0.01


def test_get_domain_insight_unknown_domain_returns_none():
    result = get_domain_insight("u1", "ghost.com")
    assert result is None


def test_get_domain_insight_excludes_active_visits():
    active = DomainVisit(
        visit_id="active-1",
        user_id="u1",
        domain="active.com",
        start_time=BASE,
    )
    add_visit(active)
    result = get_domain_insight("u1", "active.com")
    assert result is None


def test_get_domain_insight_busiest_hour():
    # 3 visits at hour 9, 1 at hour 14
    for i in range(3):
        make_closed_visit("u1", "news.com", BASE + timedelta(minutes=i * 10))
    make_closed_visit("u1", "news.com", BASE.replace(hour=14))

    insight = get_domain_insight("u1", "news.com")
    assert insight is not None
    assert insight.busiest_hour == 9


def test_get_domain_insight_first_and_last_seen():
    t1 = BASE
    t2 = BASE + timedelta(days=3)
    make_closed_visit("u1", "blog.com", t2)
    make_closed_visit("u1", "blog.com", t1)

    insight = get_domain_insight("u1", "blog.com")
    assert insight.first_seen == t1.isoformat()
    assert insight.last_seen == t2.isoformat()


def test_get_all_domain_insights_sorted_by_total_minutes():
    make_closed_visit("u2", "small.com", BASE, 60)
    make_closed_visit("u2", "big.com", BASE, 3600)
    make_closed_visit("u2", "medium.com", BASE, 600)

    insights = get_all_domain_insights("u2")
    domains = [i.domain for i in insights]
    assert domains.index("big.com") < domains.index("medium.com")
    assert domains.index("medium.com") < domains.index("small.com")


def test_get_all_domain_insights_empty_user():
    result = get_all_domain_insights("nobody")
    assert result == []
