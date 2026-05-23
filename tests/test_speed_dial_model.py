import pytest
from app.models.speed_dial import SpeedDial


def make_entry(**kwargs) -> SpeedDial:
    defaults = {"user_id": "u1", "domain": "example.com", "label": "Example"}
    defaults.update(kwargs)
    return SpeedDial(**defaults)


def test_speed_dial_defaults():
    e = make_entry()
    assert e.position == 0
    assert e.pinned is False
    assert e.last_visited_at is None
    assert e.id is not None
    assert e.created_at is not None


def test_update_label_changes_label():
    e = make_entry()
    e.update_label("New Label")
    assert e.label == "New Label"


def test_update_label_blank_raises():
    e = make_entry()
    with pytest.raises(ValueError):
        e.update_label("   ")


def test_move_to_sets_position():
    e = make_entry()
    e.move_to(5)
    assert e.position == 5


def test_move_to_negative_raises():
    e = make_entry()
    with pytest.raises(ValueError):
        e.move_to(-1)


def test_toggle_pin_flips_state():
    e = make_entry()
    assert e.pinned is False
    e.toggle_pin()
    assert e.pinned is True
    e.toggle_pin()
    assert e.pinned is False


def test_touch_sets_last_visited_at():
    e = make_entry()
    assert e.last_visited_at is None
    e.touch()
    assert e.last_visited_at is not None


def test_to_dict_roundtrip():
    e = make_entry(position=3, pinned=True)
    d = e.to_dict()
    e2 = SpeedDial.from_dict(d)
    assert e2.id == e.id
    assert e2.domain == e.domain
    assert e2.label == e.label
    assert e2.position == e.position
    assert e2.pinned == e.pinned
