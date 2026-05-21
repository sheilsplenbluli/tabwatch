import pytest
from datetime import datetime, timedelta
from app.models.domain_visit import DomainVisit


def make_visit(domain="example.com", user_id="user_1", start_offset_seconds=0):
    start = datetime(2024, 1, 15, 10, 0, 0) + timedelta(seconds=start_offset_seconds)
    return DomainVisit(domain=domain, user_id=user_id, start_time=start)


def test_new_visit_is_active():
    visit = make_visit()
    assert visit.is_active is True
    assert visit.end_time is None
    assert visit.duration_seconds == 0


def test_close_sets_end_time_and_duration():
    visit = make_visit()
    end = datetime(2024, 1, 15, 10, 5, 30)
    visit.close(end_time=end)
    assert visit.end_time == end
    assert visit.duration_seconds == 330
    assert visit.is_active is False


def test_close_without_explicit_end_time_uses_utcnow():
    visit = make_visit()
    before = datetime.utcnow()
    visit.close()
    after = datetime.utcnow()
    assert before <= visit.end_time <= after
    assert visit.duration_seconds >= 0


def test_duration_never_negative():
    # end_time before start_time edge case
    visit = make_visit()
    visit.close(end_time=datetime(2024, 1, 15, 9, 59, 0))  # 1 min before start
    assert visit.duration_seconds == 0


def test_to_dict_round_trip():
    visit = make_visit(domain="github.com", user_id="user_42")
    visit.close(end_time=datetime(2024, 1, 15, 10, 10, 0))
    visit.id = 7

    data = visit.to_dict()
    restored = DomainVisit.from_dict(data)

    assert restored.id == 7
    assert restored.domain == "github.com"
    assert restored.user_id == "user_42"
    assert restored.duration_seconds == 600
    assert restored.is_active is False


def test_to_dict_active_visit_has_no_end_time():
    visit = make_visit()
    data = visit.to_dict()
    assert data["end_time"] is None
    assert data["duration_seconds"] == 0
