import pytest
from datetime import datetime, timezone
from app.models.bookmark import Bookmark


def make_bookmark(**kwargs) -> Bookmark:
    defaults = dict(
        user_id="u1",
        domain="example.com",
        url="https://example.com/page",
        title="Example Page",
    )
    defaults.update(kwargs)
    return Bookmark(**defaults)


def test_bookmark_defaults():
    b = make_bookmark()
    assert b.pinned is False
    assert b.note == ""
    assert b.tags == []
    assert isinstance(b.created_at, datetime)


def test_update_title_changes_title():
    b = make_bookmark()
    b.update_title("  New Title  ")
    assert b.title == "New Title"


def test_update_title_blank_raises():
    b = make_bookmark()
    with pytest.raises(ValueError):
        b.update_title("   ")


def test_toggle_pin_flips_state():
    b = make_bookmark()
    assert b.toggle_pin() is True
    assert b.pinned is True
    assert b.toggle_pin() is False
    assert b.pinned is False


def test_to_dict_roundtrip():
    b = make_bookmark(note="cool site", tags=["work"], pinned=True)
    d = b.to_dict()
    b2 = Bookmark.from_dict(d)
    assert b2.bookmark_id == b.bookmark_id
    assert b2.title == b.title
    assert b2.note == "cool site"
    assert b2.tags == ["work"]
    assert b2.pinned is True


def test_from_dict_generates_id_if_missing():
    data = {
        "user_id": "u1",
        "domain": "foo.com",
        "url": "https://foo.com",
        "title": "Foo",
    }
    b = Bookmark.from_dict(data)
    assert b.bookmark_id is not None and len(b.bookmark_id) > 0
