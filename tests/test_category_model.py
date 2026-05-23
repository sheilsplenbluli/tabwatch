import pytest
from app.models.category import Category


def make_category(**kwargs) -> Category:
    defaults = {"user_id": "u1", "name": "Social", "color": "#ff0000"}
    defaults.update(kwargs)
    return Category(**defaults)


def test_category_defaults():
    cat = make_category()
    assert cat.name == "Social"
    assert cat.color == "#ff0000"
    assert cat.domains == []
    assert cat.category_id is not None


def test_add_domain_appends():
    cat = make_category()
    cat.add_domain("twitter.com")
    assert "twitter.com" in cat.domains


def test_add_domain_no_duplicates():
    cat = make_category()
    cat.add_domain("twitter.com")
    cat.add_domain("twitter.com")
    assert cat.domains.count("twitter.com") == 1


def test_remove_domain():
    cat = make_category(domains=["twitter.com", "reddit.com"])
    cat.remove_domain("twitter.com")
    assert "twitter.com" not in cat.domains
    assert "reddit.com" in cat.domains


def test_matches_domain_true():
    cat = make_category(domains=["twitter.com"])
    assert cat.matches_domain("twitter.com") is True


def test_matches_domain_false():
    cat = make_category()
    assert cat.matches_domain("github.com") is False


def test_to_dict_roundtrip():
    cat = make_category(domains=["twitter.com"])
    d = cat.to_dict()
    restored = Category.from_dict(d)
    assert restored.category_id == cat.category_id
    assert restored.name == cat.name
    assert restored.domains == cat.domains
    assert restored.color == cat.color
