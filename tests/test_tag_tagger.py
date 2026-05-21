"""Tests for app/services/tag_tagger.py"""

import pytest
from datetime import datetime, timedelta

from app.models.domain_visit import DomainVisit
from app.models.tag import Tag
from app.services import tag_store
from app.services.tag_tagger import (
    get_tags_for_domain,
    annotate_visit,
    annotate_visits,
    visits_for_tag,
)


@pytest.fixture(autouse=True)
def reset_store():
    tag_store._store.clear()
    yield
    tag_store._store.clear()


def make_visit(domain: str) -> DomainVisit:
    v = DomainVisit(user_id="u1", domain=domain)
    v.tags = []
    return v


def make_tag(name: str, domains: list) -> Tag:
    t = tag_store.create_tag("u1", name)
    for d in domains:
        t.add_domain(d)
    tag_store.update_tag("u1", t.tag_id, t)
    return t


def test_get_tags_for_domain_returns_matching():
    make_tag("social", ["twitter.com", "facebook.com"])
    make_tag("news", ["bbc.com"])
    result = get_tags_for_domain("u1", "twitter.com")
    assert "social" in result
    assert "news" not in result


def test_get_tags_for_domain_no_match_returns_empty():
    make_tag("social", ["twitter.com"])
    result = get_tags_for_domain("u1", "github.com")
    assert result == []


def test_annotate_visit_attaches_tags():
    make_tag("work", ["github.com", "jira.com"])
    visit = make_visit("github.com")
    annotate_visit("u1", visit)
    assert "work" in visit.tags


def test_annotate_visit_no_duplicate_tags():
    make_tag("work", ["github.com"])
    visit = make_visit("github.com")
    visit.tags = ["work"]
    annotate_visit("u1", visit)
    assert visit.tags.count("work") == 1


def test_annotate_visits_processes_all():
    make_tag("social", ["twitter.com"])
    make_tag("work", ["github.com"])
    visits = [make_visit("twitter.com"), make_visit("github.com"), make_visit("bbc.com")]
    result = annotate_visits("u1", visits)
    assert "social" in result[0].tags
    assert "work" in result[1].tags
    assert result[2].tags == []


def test_visits_for_tag_filters_correctly():
    make_tag("social", ["twitter.com", "instagram.com"])
    visits = [make_visit("twitter.com"), make_visit("github.com"), make_visit("instagram.com")]
    result = visits_for_tag("u1", "social", visits)
    domains = [v.domain for v in result]
    assert "twitter.com" in domains
    assert "instagram.com" in domains
    assert "github.com" not in domains


def test_visits_for_tag_unknown_tag_returns_empty():
    visits = [make_visit("twitter.com")]
    result = visits_for_tag("u1", "nonexistent", visits)
    assert result == []
