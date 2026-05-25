import pytest
from flask import Flask
from app.api.custom_report_routes import bp
from app.services import custom_report_store as store
from app.models.custom_report import CustomReport


@pytest.fixture(autouse=True)
def reset_store():
    store.clear_all()
    yield
    store.clear_all()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    return app.test_client()


def make_report(**kwargs):
    defaults = dict(
        user_id="u1",
        name="My Report",
        domains=["github.com", "stackoverflow.com"],
        start_iso="2024-01-01T00:00:00",
        end_iso="2024-01-07T23:59:59",
    )
    defaults.update(kwargs)
    return CustomReport(**defaults)


def test_create_report_success(client):
    resp = client.post("/reports/", json={
        "user_id": "u1",
        "name": "Weekly Report",
        "domains": ["github.com"],
        "start_iso": "2024-01-01T00:00:00",
        "end_iso": "2024-01-07T23:59:59",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Weekly Report"
    assert "report_id" in data


def test_create_report_missing_field(client):
    resp = client.post("/reports/", json={"user_id": "u1", "name": "X"})
    assert resp.status_code == 400


def test_create_report_empty_domains_raises(client):
    resp = client.post("/reports/", json={
        "user_id": "u1",
        "name": "Bad",
        "domains": [],
        "start_iso": "2024-01-01T00:00:00",
        "end_iso": "2024-01-07T23:59:59",
    })
    assert resp.status_code == 400


def test_list_reports_for_user(client):
    r = make_report()
    store.add_report(r)
    resp = client.get("/reports/?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_list_reports_missing_user_id(client):
    resp = client.get("/reports/")
    assert resp.status_code == 400


def test_edit_report_name(client):
    r = make_report()
    store.add_report(r)
    resp = client.put(f"/reports/{r.report_id}", json={"name": "Updated"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Updated"


def test_edit_report_not_found(client):
    resp = client.put("/reports/nonexistent", json={"name": "X"})
    assert resp.status_code == 404


def test_delete_report(client):
    r = make_report()
    store.add_report(r)
    resp = client.delete(f"/reports/{r.report_id}")
    assert resp.status_code == 200
    assert store.get_report(r.report_id) is None


def test_delete_report_not_found(client):
    resp = client.delete("/reports/ghost")
    assert resp.status_code == 404


def test_report_model_blank_name_raises():
    with pytest.raises(ValueError):
        CustomReport(user_id="u1", name="  ", domains=["x.com"],
                     start_iso="2024-01-01T00:00:00", end_iso="2024-01-07T23:59:59")


def test_report_roundtrip():
    r = make_report(description="test desc")
    restored = CustomReport.from_dict(r.to_dict())
    assert restored.report_id == r.report_id
    assert restored.description == "test desc"
    assert restored.domains == r.domains
