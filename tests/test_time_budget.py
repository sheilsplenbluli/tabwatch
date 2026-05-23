import pytest
from datetime import datetime, timezone
from app.models.time_budget import TimeBudget
from app.services import time_budget_store, visit_store
from app.models.domain_visit import DomainVisit
from app.api import create_app


@pytest.fixture(autouse=True)
def reset_store():
    time_budget_store.clear_all()
    visit_store.clear_all()
    yield
    time_budget_store.clear_all()
    visit_store.clear_all()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, duration_seconds=600):
    v = DomainVisit(user_id=user_id, domain=domain)
    v.start_time = datetime.now(timezone.utc)
    v.close(duration_override=duration_seconds)
    visit_store.add_visit(v)
    return v


def test_budget_is_exceeded_when_over_limit():
    b = TimeBudget(user_id="u1", domain="example.com", daily_limit_minutes=10)
    assert b.is_exceeded(10) is True
    assert b.is_exceeded(9.9) is False


def test_percent_used_calculation():
    b = TimeBudget(user_id="u1", domain="example.com", daily_limit_minutes=60)
    assert b.percent_used(30) == 50.0
    assert b.percent_used(0) == 0.0


def test_to_dict_and_from_dict_roundtrip():
    b = TimeBudget(user_id="u1", domain="news.com", daily_limit_minutes=30, label="news")
    restored = TimeBudget.from_dict(b.to_dict())
    assert restored.domain == b.domain
    assert restored.daily_limit_minutes == b.daily_limit_minutes
    assert restored.label == b.label


def test_create_budget_success(client):
    resp = client.post("/budgets/u1", json={"domain": "youtube.com", "daily_limit_minutes": 45})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "youtube.com"
    assert data["daily_limit_minutes"] == 45


def test_create_budget_missing_field(client):
    resp = client.post("/budgets/u1", json={"domain": "youtube.com"})
    assert resp.status_code == 400


def test_list_budgets_for_user(client):
    client.post("/budgets/u1", json={"domain": "a.com", "daily_limit_minutes": 20})
    client.post("/budgets/u1", json={"domain": "b.com", "daily_limit_minutes": 10})
    resp = client.get("/budgets/u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_delete_budget(client):
    r = client.post("/budgets/u1", json={"domain": "x.com", "daily_limit_minutes": 15})
    bid = r.get_json()["budget_id"]
    resp = client.delete(f"/budgets/u1/{bid}")
    assert resp.status_code == 200
    assert resp.get_json()["deleted"] == bid


def test_check_budget_not_exceeded(client):
    make_closed_visit("u1", "slow.com", duration_seconds=120)
    client.post("/budgets/u1", json={"domain": "slow.com", "daily_limit_minutes": 60})
    resp = client.get("/budgets/u1/check/slow.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["exceeded"] is False
    assert data["has_budget"] is True


def test_check_budget_no_budget_for_domain(client):
    resp = client.get("/budgets/u1/check/unknown.com")
    assert resp.status_code == 200
    assert resp.get_json()["has_budget"] is False
