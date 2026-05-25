import pytest
from app.services.domain_ignore import (
    add_ignored,
    remove_ignored,
    is_ignored,
    get_ignored_for_user,
    clear_all,
)


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    yield
    clear_all()


def test_add_ignored_creates_entry():
    entry = add_ignored("u1", "twitter.com")
    assert entry.domain == "twitter.com"
    assert entry.user_id == "u1"
    assert entry.entry_id is not None


def test_add_ignored_with_reason():
    entry = add_ignored("u1", "reddit.com", reason="too distracting")
    assert entry.reason == "too distracting"


def test_add_ignored_no_duplicates():
    e1 = add_ignored("u1", "twitter.com")
    e2 = add_ignored("u1", "twitter.com")
    assert e1.entry_id == e2.entry_id
    assert len(get_ignored_for_user("u1")) == 1


def test_is_ignored_returns_true_when_present():
    add_ignored("u1", "facebook.com")
    assert is_ignored("u1", "facebook.com") is True


def test_is_ignored_returns_false_when_absent():
    assert is_ignored("u1", "github.com") is False


def test_is_ignored_isolates_by_user():
    add_ignored("u1", "tiktok.com")
    assert is_ignored("u2", "tiktok.com") is False


def test_remove_ignored_returns_true_and_removes():
    add_ignored("u1", "youtube.com")
    result = remove_ignored("u1", "youtube.com")
    assert result is True
    assert is_ignored("u1", "youtube.com") is False


def test_remove_ignored_unknown_returns_false():
    result = remove_ignored("u1", "nothere.com")
    assert result is False


def test_get_ignored_for_user_returns_all():
    add_ignored("u1", "a.com")
    add_ignored("u1", "b.com")
    add_ignored("u2", "c.com")
    entries = get_ignored_for_user("u1")
    domains = {e.domain for e in entries}
    assert domains == {"a.com", "b.com"}


def test_to_dict_contains_expected_keys():
    entry = add_ignored("u1", "example.com", reason="test")
    d = entry.to_dict()
    assert set(d.keys()) == {"entry_id", "user_id", "domain", "reason", "created_at"}
    assert d["domain"] == "example.com"
    assert d["reason"] == "test"
