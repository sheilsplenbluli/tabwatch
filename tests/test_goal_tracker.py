import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from app.services.goal_tracker import (
    set_goal, get_goal, get_goals_for_user,
    delete_goal, check_goal_progress, clear_all_goals,
)
from app.api import create_app
from app.services.visit_store import add_visit, clear_visits
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    clear_all_goals()
    clear_visits()
    yield
    clear_all_goals()
    clear_visits()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, duration_seconds=600):
    now = datetime.now(timezone.utc)
    v = DomainVisit(user_id=user_id, domain=domain, start_time=now)
    v.close(end_time=now)
    v.duration_seconds = duration_seconds
    add_visit(v)
    return v


def test_set_and_get_goal():
    goal = set_goal("u1", "example.com", 30)
    assert goal["daily_limit_minutes"] == 30
    fetched = get_goal("u1", "example.com")
    assert fetched is not None
    assert fetched["domain"] == "example.com"


def test_get_goal_unknown_returns_none():
    assert get_goal("u1", "nope.com") is None


def test_set_goal_invalid_limit_raises():
    with pytest.raises(ValueError):
        set_goal("u1", "example.com", 0)


def test_get_goals_for_user_lists_all():
    set_goal("u1", "a.com", 10)
    set_goal("u1", "b.com", 20)
    goals = get_goals_for_user("u1")
    domains = {g["domain"] for g in goals}
    assert domains == {"a.com", "b.com"}


def test_delete_goal_removes_it():
    set_goal("u1", "x.com", 15)
    assert delete_goal("u1", "x.com") is True
    assert get_goal("u1", "x.com") is None


def test_delete_goal_not_found_returns_false():
    assert delete_goal("u1", "ghost.com") is False


def test_check_goal_progress_over_limit():
    set_goal("u1", "news.com", 5)
    make_closed_visit("u1", "news.com", duration_seconds=600)  # 10 minutes
    result = check_goal_progress("u1", "news.com")
    assert result["over_limit"] is True
    assert result["minutes_today"] == pytest.approx(10.0, 0.1)
    assert result["percent_used"] == pytest.approx(200.0, 0.1)


def test_check_goal_progress_under_limit():
    set_goal("u1", "work.com", 60)
    make_closed_visit("u1", "work.com", duration_seconds=900)  # 15 min
    result = check_goal_progress("u1", "work.com")
    assert result["over_limit"] is False
    assert result["percent_used"] == pytest.approx(25.0, 0.1)


def test_check_goal_no_goal_returns_none():
    assert check_goal_progress("u1", "unknown.com") is None


def test_upsert_goal_route(client):
    resp = client.put("/goals/u1/example.com", json={"daily_limit_minutes": 45})
    assert resp.status_code == 200
    assert resp.get_json()["daily_limit_minutes"] == 45


def test_upsert_goal_missing_field(client):
    resp = client.put("/goals/u1/example.com", json={})
    assert resp.status_code == 400


def test_delete_goal_route(client):
    client.put("/goals/u1/bye.com", json={"daily_limit_minutes": 10})
    resp = client.delete("/goals/u1/bye.com")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] is True


def test_progress_route_no_goal(client):
    resp = client.get("/goals/u1/nope.com/progress")
    assert resp.status_code == 404
