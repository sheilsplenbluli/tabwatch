from datetime import datetime, timezone, timedelta
import pytest

from app.models.domain_visit import DomainVisit
from app.models.weekly_digest import WeeklyDigest, DomainSummary
from app.services.digest_builder import build_digest, format_digest_text, get_week_start


MONDAY = datetime(2024, 1, 8, 0, 0, 0, tzinfo=timezone.utc)


def make_closed_visit(domain: str, start: datetime, duration_seconds: float) -> DomainVisit:
    visit = DomainVisit(domain=domain, start_time=start)
    visit.close(end_time=start + timedelta(seconds=duration_seconds))
    return visit


def test_digest_aggregates_visits_by_domain():
    visits = [
        make_closed_visit("github.com", MONDAY + timedelta(hours=1), 600),
        make_closed_visit("github.com", MONDAY + timedelta(hours=3), 300),
        make_closed_visit("news.ycombinator.com", MONDAY + timedelta(hours=2), 120),
    ]
    digest = build_digest("user1", visits, week_start=MONDAY)
    assert len(digest.summaries) == 2
    gh = next(s for s in digest.summaries if s.domain == "github.com")
    assert gh.total_seconds == 900
    assert gh.visit_count == 2


def test_digest_excludes_visits_outside_week():
    outside = make_closed_visit("old.com", MONDAY - timedelta(days=1), 500)
    inside = make_closed_visit("new.com", MONDAY + timedelta(days=2), 200)
    digest = build_digest("user2", [outside, inside], week_start=MONDAY)
    domains = [s.domain for s in digest.summaries]
    assert "new.com" in domains
    assert "old.com" not in domains


def test_digest_excludes_active_visits():
    active = DomainVisit(domain="active.com", start_time=MONDAY + timedelta(hours=1))
    closed = make_closed_visit("closed.com", MONDAY + timedelta(hours=2), 60)
    digest = build_digest("user3", [active, closed], week_start=MONDAY)
    domains = [s.domain for s in digest.summaries]
    assert "active.com" not in domains
    assert "closed.com" in domains


def test_top_domains_limits_results():
    visits = [
        make_closed_visit(f"site{i}.com", MONDAY + timedelta(hours=i), 100 * i)
        for i in range(1, 8)
    ]
    digest = build_digest("user4", visits, week_start=MONDAY)
    assert len(digest.top_domains(3)) == 3


def test_total_tracked_seconds():
    visits = [
        make_closed_visit("a.com", MONDAY, 300),
        make_closed_visit("b.com", MONDAY + timedelta(hours=1), 700),
    ]
    digest = build_digest("user5", visits, week_start=MONDAY)
    assert digest.total_tracked_seconds() == 1000


def test_format_digest_text_contains_key_info():
    visits = [make_closed_visit("example.com", MONDAY + timedelta(hours=1), 3600)]
    digest = build_digest("alice", visits, week_start=MONDAY)
    text = format_digest_text(digest)
    assert "alice" in text
    assert "example.com" in text
    assert "60.0 min" in text


def test_get_week_start_returns_monday():
    wednesday = datetime(2024, 1, 10, 14, 30, tzinfo=timezone.utc)
    result = get_week_start(wednesday)
    assert result.weekday() == 0
    assert result.hour == 0 and result.minute == 0
    assert result == datetime(2024, 1, 8, tzinfo=timezone.utc)
