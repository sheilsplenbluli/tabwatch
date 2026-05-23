import pytest
from datetime import datetime, timedelta
from app.services.badge_engine import (
    evaluate_badges,
    get_badges_for_user,
    get_unseen_badges,
    mark_badges_seen,
    clear_all_badges,
)
from app.services.visit_store import add_visit, clear_visits
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    clear_all_badges()
    clear_visits()
    yield
    clear_all_badges()
    clear_visits()


def make_closed_visit(user_id="u1", domain="example.com", minutes=10):
    start = datetime.utcnow() - timedelta(minutes=minutes)
    end = datetime.utcnow()
    v = DomainVisit(visit_id=f"v-{domain}-{minutes}", user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=end)
    add_visit(v)
    return v


def test_no_visits_no_badges_earned():
    newly = evaluate_badges("u1")
    assert newly == []


def test_first_visit_badge_earned():
    make_closed_visit()
    newly = evaluate_badges("u1")
    ids = [b.badge_id for b in newly]
    assert "first_visit" in ids


def test_evaluate_is_idempotent():
    make_closed_visit()
    evaluate_badges("u1")
    newly_second = evaluate_badges("u1")
    # first_visit should not appear again
    ids = [b.badge_id for b in newly_second]
    assert "first_visit" not in ids


def test_century_badge_requires_100_visits():
    for i in range(99):
        make_closed_visit(user_id="u2", domain=f"site{i}.com", minutes=1)
    newly = evaluate_badges("u2")
    ids = [b.badge_id for b in newly]
    assert "century" not in ids

    make_closed_visit(user_id="u2", domain="site100.com", minutes=1)
    newly2 = evaluate_badges("u2")
    ids2 = [b.badge_id for b in newly2]
    assert "century" in ids2


def test_get_unseen_badges_after_earn():
    make_closed_visit()
    evaluate_badges("u1")
    unseen = get_unseen_badges("u1")
    assert any(b.badge_id == "first_visit" for b in unseen)


def test_mark_badges_seen_clears_unseen():
    make_closed_visit()
    evaluate_badges("u1")
    mark_badges_seen("u1")
    unseen = get_unseen_badges("u1")
    assert unseen == []


def test_get_badges_for_user_returns_all_definitions():
    badges = get_badges_for_user("u1")
    ids = {b.badge_id for b in badges}
    assert {"first_visit", "streak_3", "streak_7", "century"}.issubset(ids)
