import pytest
from datetime import datetime, timezone
from app.models.whitelist import WhitelistEntry


def make_entry(**kwargs) -> WhitelistEntry:
    defaults = {"user_id": "u1", "domain": "example.com"}
    defaults.update(kwargs)
    return WhitelistEntry(**defaults)


def test_whitelist_entry_defaults():
    e = make_entry()
    assert e.user_id == "u1"
    assert e.domain == "example.com"
    assert e.label is None
    assert isinstance(e.added_at, datetime)


def test_whitelist_entry_with_label():
    e = make_entry(label="work")
    assert e.label == "work"


def test_to_dict_contains_expected_keys():
    e = make_entry(label="news")
    d = e.to_dict()
    assert d["user_id"] == "u1"
    assert d["domain"] == "example.com"
    assert d["label"] == "news"
    assert "added_at" in d


def test_from_dict_roundtrip():
    e = make_entry(label="social")
    restored = WhitelistEntry.from_dict(e.to_dict())
    assert restored.user_id == e.user_id
    assert restored.domain == e.domain
    assert restored.label == e.label


def test_matches_is_case_insensitive():
    e = make_entry(domain="GitHub.com")
    assert e.matches("github.com")
    assert e.matches("GITHUB.COM")
    assert not e.matches("gitlab.com")
