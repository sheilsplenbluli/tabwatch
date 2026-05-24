import pytest
from datetime import datetime, timedelta
from app.api import create_app
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


NOW = datetime(2024, 6, 1, 10, 0, 0)


def make_closed_visit(user_id, domain, start, duration_minutes=5):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    v.close(start + timedelta(minutes=duration_minutes))
    add_visit(v)
    return v


def test_list_clusters_missing_user_id(client):
    resp = client.get("/clustering/")
    assert resp.status_code == 400


def test_list_clusters_returns_empty_for_no_visits(client):
    resp = client.get("/clustering/?user_id=u1")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_list_clusters_returns_cluster(client):
    make_closed_visit("u1", "a.com", NOW)
    make_closed_visit("u1", "b.com", NOW + timedelta(minutes=5))
    resp = client.get("/clustering/?user_id=u1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert set(data[0]["domains"]) == {"a.com", "b.com"}


def test_cluster_for_domain_missing_params(client):
    resp = client.get("/clustering/domain?user_id=u1")
    assert resp.status_code == 400


def test_cluster_for_domain_not_found(client):
    resp = client.get("/clustering/domain?user_id=u1&domain=nope.com")
    assert resp.status_code == 404


def test_cluster_for_domain_returns_cluster(client):
    make_closed_visit("u1", "a.com", NOW)
    make_closed_visit("u1", "b.com", NOW + timedelta(minutes=5))
    resp = client.get("/clustering/domain?user_id=u1&domain=a.com")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "b.com" in data["domains"]
    assert data["user_id"] == "u1"
