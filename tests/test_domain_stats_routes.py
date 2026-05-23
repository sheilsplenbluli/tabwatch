import pytest
from datetime import datetime, timezone, timedelta
from app import create_app
from app.services import visit_store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    visit_store._store.clear()
    visit_store._counter = 0
    yield
    visit_store._store.clear()
    visit_store._counter = 0


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(user_id, domain, start, duration_seconds):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(end_time=start + timedelta(seconds=duration_seconds))
    visit_store.add_visit(v)
    return v


START = "2024-06-03T00:00:00"
END = "2024-06-09T23:59:59"


def test_summary_returns_200(client):
    make_closed_visit(
        "u1", "a.com",
        datetime(2024, 6, 3, 10, 0, tzinfo=timezone.utc), 300
    )
    resp = client.get(f"/stats/u1/summary?start={START}&end={END}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_seconds"] == 300.0
    assert "busiest_hour" in data


def test_summary_missing_params_returns_400(client):
    resp = client.get("/stats/u1/summary?start=2024-06-03T00:00:00")
    assert resp.status_code == 400


def test_summary_invalid_datetime_returns_400(client):
    resp = client.get("/stats/u1/summary?start=not-a-date&end=also-bad")
    assert resp.status_code == 400


def test_busiest_hour_no_visits(client):
    resp = client.get(f"/stats/u1/busiest-hour?start={START}&end={END}")
    assert resp.status_code == 200
    assert resp.get_json()["busiest_hour"] is None


def test_busiest_hour_with_visits(client):
    make_closed_visit(
        "u1", "a.com",
        datetime(2024, 6, 3, 15, 0, tzinfo=timezone.utc), 600
    )
    resp = client.get(f"/stats/u1/busiest-hour?start={START}&end={END}")
    assert resp.status_code == 200
    assert resp.get_json()["busiest_hour"] == 15


def test_domain_count_endpoint(client):
    make_closed_visit(
        "u1", "news.com",
        datetime(2024, 6, 4, 9, 0, tzinfo=timezone.utc), 60
    )
    make_closed_visit(
        "u1", "news.com",
        datetime(2024, 6, 5, 9, 0, tzinfo=timezone.utc), 60
    )
    resp = client.get(f"/stats/u1/domain-count?domain=news.com&start={START}&end={END}")
    assert resp.status_code == 200
    assert resp.get_json()["visit_count"] == 2


def test_domain_count_missing_domain_returns_400(client):
    resp = client.get(f"/stats/u1/domain-count?start={START}&end={END}")
    assert resp.status_code == 400
