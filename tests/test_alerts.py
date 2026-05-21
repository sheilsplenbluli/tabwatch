import pytest
from datetime import datetime, timezone, timedelta
from app.models.alert_rule import AlertRule
from app.models.domain_visit import DomainVisit
from app.services.alert_store import add_rule, clear_all, get_rules_for_user, delete_rule
from app.services.alert_checker import check_alerts_for_user, format_alert_message
from app.api import create_app


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    yield
    clear_all()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def make_closed_visit(domain, minutes, offset_minutes=0):
    now = datetime.now(timezone.utc) - timedelta(minutes=offset_minutes)
    start = now - timedelta(minutes=minutes)
    v = DomainVisit(user_id="u1", domain=domain, start_time=start)
    v.close(end_time=now)
    return v


def test_alert_rule_triggered_at_limit():
    rule = AlertRule(user_id="u1", domain="youtube.com", daily_limit_minutes=30)
    assert rule.is_triggered(30.0) is True
    assert rule.is_triggered(29.9) is False


def test_alert_rule_notify_at_percent():
    rule = AlertRule(user_id="u1", domain="reddit.com", daily_limit_minutes=60, notify_at_percent=80)
    assert rule.is_triggered(48.0) is True
    assert rule.is_triggered(47.9) is False


def test_disabled_rule_never_triggers():
    rule = AlertRule(user_id="u1", domain="x.com", daily_limit_minutes=10, enabled=False)
    assert rule.is_triggered(999) is False


def test_check_alerts_returns_triggered(reset_store):
    add_rule(AlertRule(user_id="u1", domain="youtube.com", daily_limit_minutes=20))
    visits = [make_closed_visit("youtube.com", 25)]
    triggered = check_alerts_for_user("u1", visits)
    assert len(triggered) == 1
    assert triggered[0][0].domain == "youtube.com"


def test_check_alerts_skips_other_domains(reset_store):
    add_rule(AlertRule(user_id="u1", domain="youtube.com", daily_limit_minutes=20))
    visits = [make_closed_visit("github.com", 60)]
    triggered = check_alerts_for_user("u1", visits)
    assert triggered == []


def test_format_alert_message():
    rule = AlertRule(user_id="u1", domain="reddit.com", daily_limit_minutes=60)
    msg = format_alert_message(rule, 60.0)
    assert "reddit.com" in msg
    assert "60" in msg
    assert "100%" in msg


def test_create_and_list_rules_via_api(client):
    resp = client.post("/alerts/u1", json={"domain": "twitch.tv", "daily_limit_minutes": 45})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["domain"] == "twitch.tv"

    resp2 = client.get("/alerts/u1")
    assert resp2.status_code == 200
    assert len(resp2.get_json()) == 1


def test_delete_rule_via_api(client):
    resp = client.post("/alerts/u1", json={"domain": "twitch.tv", "daily_limit_minutes": 45})
    rule_id = resp.get_json()["rule_id"]
    del_resp = client.delete(f"/alerts/u1/{rule_id}")
    assert del_resp.status_code == 200
    assert get_rules_for_user("u1") == []


def test_create_rule_missing_field(client):
    resp = client.post("/alerts/u1", json={"domain": "twitch.tv"})
    assert resp.status_code == 400
