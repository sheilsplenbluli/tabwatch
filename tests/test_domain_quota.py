"""Tests for domain quota service and routes."""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from app.api import create_app
from app.services.domain_quota import (
    check_quota,
    clear_all_quotas,
    delete_quota,
    get_quota,
    get_quotas_for_user,
    set_quota,
)
from app.services.visit_store import add_visit, get_all_visits
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    clear_all_quotas()
    from app.services import visit_store
    visit_store._store.clear()
    visit_store._id_counter = 0
    yield
    clear_all_quotas()
    visit_store._store.clear()
    visit_store._id_counter = 0


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, minutes=10):
    from datetime import timedelta
    start = datetime.now(timezone.utc)
    end = start + timedelta(minutes=minutes)
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=end)
    add_visit(v)
    return v


def test_set_and_get_quota():
    set_quota("u1", "example.com", 5)
    assert get_quota("u1", "example.com") == 5


def test_get_quota_unknown_returns_none():
    assert get_quota("u1", "unknown.com") is None


def test_set_quota_invalid_limit_raises():
    with pytest.raises(ValueError):
        set_quota("u1", "example.com", 0)


def test_delete_quota_removes_entry():
    set_quota("u1", "example.com", 3)
    assert delete_quota("u1", "example.com") is True
    assert get_quota("u1", "example.com") is None


def test_delete_quota_unknown_returns_false():
    assert delete_quota("u1", "nope.com") is False


def test_get_quotas_for_user_filters_correctly():
    set_quota("u1", "a.com", 2)
    set_quota("u1", "b.com", 4)
    set_quota("u2", "a.com", 1)
    result = get_quotas_for_user("u1")
    assert result == {"a.com": 2, "b.com": 4}


def test_check_quota_not_exceeded():
    set_quota("u1", "example.com", 5)
    status = check_quota("u1", "example.com")
    assert status is not None
    assert status.exceeded is False
    assert status.remaining == 5


def test_check_quota_exceeded_when_at_limit():
    set_quota("u1", "example.com", 1)
    make_closed_visit("u1", "example.com")
    status = check_quota("u1", "example.com")
    assert status.exceeded is True
    assert status.remaining == 0


def test_check_quota_returns_none_when_no_quota_set():
    assert check_quota("u1", "nodomain.com") is None


def test_route_upsert_and_check(client):
    r = client.put("/quota/u1/example.com", json={"daily_limit": 3})
    assert r.status_code == 200
    r2 = client.get("/quota/u1/example.com/check")
    assert r2.status_code == 200
    data = r2.get_json()
    assert data["daily_limit"] == 3
    assert data["exceeded"] is False


def test_route_upsert_missing_field(client):
    r = client.put("/quota/u1/example.com", json={})
    assert r.status_code == 400


def test_route_delete_quota(client):
    client.put("/quota/u1/example.com", json={"daily_limit": 2})
    r = client.delete("/quota/u1/example.com")
    assert r.status_code == 200
    r2 = client.delete("/quota/u1/example.com")
    assert r2.status_code == 404


def test_route_check_no_quota_returns_404(client):
    r = client.get("/quota/u1/nodomain.com/check")
    assert r.status_code == 404
