import pytest
from flask import Flask
from app.models.focus_goal import FocusGoal
import app.services.focus_goal_store as store
from app.api.focus_goal_routes import bp


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
    with app.test_client() as c:
        yield c


def make_goal(user_id="u1", label="Focus session", target_minutes=30, domains=None):
    return FocusGoal(
        user_id=user_id,
        label=label,
        target_minutes=target_minutes,
        domains=domains or ["github.com"],
    )


def test_focus_goal_defaults():
    g = make_goal()
    assert g.is_active is True
    assert g.completed_at is None
    assert g.is_completed() is False


def test_focus_goal_invalid_target_raises():
    with pytest.raises(ValueError):
        FocusGoal(user_id="u1", label="x", target_minutes=0)


def test_focus_goal_blank_label_raises():
    with pytest.raises(ValueError):
        FocusGoal(user_id="u1", label="  ", target_minutes=10)


def test_complete_sets_flags():
    g = make_goal()
    g.complete()
    assert g.is_completed() is True
    assert g.is_active is False
    assert g.completed_at is not None


def test_complete_is_idempotent():
    g = make_goal()
    g.complete()
    first_time = g.completed_at
    g.complete()
    assert g.completed_at == first_time


def test_to_dict_roundtrip():
    g = make_goal()
    d = g.to_dict()
    g2 = FocusGoal.from_dict(d)
    assert g2.goal_id == g.goal_id
    assert g2.label == g.label
    assert g2.target_minutes == g.target_minutes


def test_create_goal_success(client):
    resp = client.post("/focus-goals", json={
        "user_id": "u1", "label": "Deep work", "target_minutes": 60,
        "domains": ["notion.so"]
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["label"] == "Deep work"
    assert data["target_minutes"] == 60


def test_create_goal_missing_field(client):
    resp = client.post("/focus-goals", json={"user_id": "u1"})
    assert resp.status_code == 400


def test_list_goals_for_user(client):
    g = make_goal()
    store.add_goal(g)
    resp = client.get("/focus-goals?user_id=u1")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1


def test_list_active_only(client):
    g1 = make_goal(label="Active")
    g2 = make_goal(label="Done")
    g2.complete()
    store.add_goal(g1)
    store.add_goal(g2)
    resp = client.get("/focus-goals?user_id=u1&active_only=true")
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["label"] == "Active"


def test_complete_goal_route(client):
    g = make_goal()
    store.add_goal(g)
    resp = client.post(f"/focus-goals/{g.goal_id}/complete")
    assert resp.status_code == 200
    assert resp.get_json()["is_active"] is False


def test_delete_goal(client):
    g = make_goal()
    store.add_goal(g)
    resp = client.delete(f"/focus-goals/{g.goal_id}")
    assert resp.status_code == 200
    assert store.get_goal(g.goal_id) is None
