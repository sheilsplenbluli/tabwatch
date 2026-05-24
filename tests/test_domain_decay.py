import pytest
from datetime import datetime, timezone, timedelta
from app.services.domain_decay import compute_decay_scores, get_decay_score_for_domain, _decay_weight
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(user_id, domain, end_offset_days=0, duration=10):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=end_offset_days, minutes=duration)
    end = now - timedelta(days=end_offset_days)
    v = DomainVisit(visit_id=f"{user_id}-{domain}-{end_offset_days}",
                    user_id=user_id, domain=domain,
                    start_time=start.isoformat(), end_time=end.isoformat(),
                    duration_seconds=duration * 60)
    add_visit(v)
    return v


def test_decay_weight_recent_is_near_one():
    now = datetime.now(timezone.utc)
    recent = now - timedelta(hours=1)
    w = _decay_weight(recent, now)
    assert 0.99 < w <= 1.0


def test_decay_weight_after_half_life_is_half():
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=7)
    w = _decay_weight(old, now)
    assert abs(w - 0.5) < 0.001


def test_compute_decay_scores_empty_returns_empty():
    result = compute_decay_scores("user1")
    assert result == []


def test_compute_decay_scores_excludes_active_visits():
    v = DomainVisit(visit_id="v1", user_id="u1", domain="example.com",
                    start_time=datetime.now(timezone.utc).isoformat())
    add_visit(v)
    result = compute_decay_scores("u1")
    assert result == []


def test_compute_decay_scores_aggregates_by_domain():
    make_closed_visit("u1", "github.com", end_offset_days=0)
    make_closed_visit("u1", "github.com", end_offset_days=1)
    make_closed_visit("u1", "news.com", end_offset_days=3)
    scores = compute_decay_scores("u1")
    domains = [s.domain for s in scores]
    assert "github.com" in domains
    assert "news.com" in domains
    github_score = next(s for s in scores if s.domain == "github.com")
    assert github_score.visit_count == 2


def test_compute_decay_scores_sorted_by_score_descending():
    make_closed_visit("u2", "recent.com", end_offset_days=0)
    make_closed_visit("u2", "old.com", end_offset_days=30)
    scores = compute_decay_scores("u2")
    assert scores[0].domain == "recent.com"
    assert scores[1].domain == "old.com"
    assert scores[0].score > scores[1].score


def test_get_decay_score_for_domain_found():
    make_closed_visit("u3", "target.com", end_offset_days=2)
    result = get_decay_score_for_domain("u3", "target.com")
    assert result is not None
    assert result.domain == "target.com"
    assert result.visit_count == 1


def test_get_decay_score_for_domain_not_found():
    result = get_decay_score_for_domain("u3", "unknown.com")
    assert result is None


def test_compute_decay_scores_only_own_user(client=None):
    make_closed_visit("userA", "shared.com", end_offset_days=0)
    make_closed_visit("userB", "shared.com", end_offset_days=0)
    scores_a = compute_decay_scores("userA")
    assert all(True for s in scores_a)  # just checks no cross-user bleed via visit_count
    score = next((s for s in scores_a if s.domain == "shared.com"), None)
    assert score is not None
    assert score.visit_count == 1
