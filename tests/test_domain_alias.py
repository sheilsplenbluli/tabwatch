import pytest
from app.services.domain_alias import (
    create_alias,
    get_alias,
    get_aliases_for_user,
    delete_alias,
    resolve_domain,
    clear_all,
    DomainAlias,
)


@pytest.fixture(autouse=True)
def reset_store():
    clear_all()
    yield
    clear_all()


def test_create_alias_stores_entry():
    entry = create_alias("u1", "google.com", ["mail.google.com", "www.google.com"])
    assert get_alias(entry.alias_id) is entry


def test_get_alias_unknown_returns_none():
    assert get_alias("does-not-exist") is None


def test_add_alias_appends():
    entry = create_alias("u1", "google.com")
    entry.add_alias("mail.google.com")
    assert "mail.google.com" in entry.aliases


def test_add_alias_no_duplicates():
    entry = create_alias("u1", "google.com", ["mail.google.com"])
    entry.add_alias("mail.google.com")
    assert entry.aliases.count("mail.google.com") == 1


def test_remove_alias_removes_entry():
    entry = create_alias("u1", "google.com", ["mail.google.com"])
    entry.remove_alias("mail.google.com")
    assert "mail.google.com" not in entry.aliases


def test_resolves_canonical():
    entry = create_alias("u1", "google.com", ["mail.google.com"])
    assert entry.resolves("google.com") is True


def test_resolves_alias():
    entry = create_alias("u1", "google.com", ["mail.google.com"])
    assert entry.resolves("mail.google.com") is True


def test_resolves_unknown_returns_false():
    entry = create_alias("u1", "google.com", ["mail.google.com"])
    assert entry.resolves("bing.com") is False


def test_get_aliases_for_user_filters_by_user():
    create_alias("u1", "google.com")
    create_alias("u2", "bing.com")
    results = get_aliases_for_user("u1")
    assert len(results) == 1
    assert results[0].canonical == "google.com"


def test_delete_alias_removes_from_store():
    entry = create_alias("u1", "google.com")
    assert delete_alias(entry.alias_id) is True
    assert get_alias(entry.alias_id) is None


def test_delete_alias_unknown_returns_false():
    assert delete_alias("ghost") is False


def test_resolve_domain_returns_canonical():
    create_alias("u1", "google.com", ["mail.google.com"])
    assert resolve_domain("u1", "mail.google.com") == "google.com"


def test_resolve_domain_passthrough_when_no_alias():
    assert resolve_domain("u1", "example.com") == "example.com"


def test_to_dict_roundtrip():
    entry = create_alias("u1", "google.com", ["mail.google.com"])
    restored = DomainAlias.from_dict(entry.to_dict())
    assert restored.alias_id == entry.alias_id
    assert restored.canonical == entry.canonical
    assert restored.aliases == entry.aliases
