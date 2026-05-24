import pytest
from datetime import datetime, timedelta
from app.services.domain_clustering import (
    compute_clusters,
    get_cluster_for_domain,
    _split_into_sessions,
)
from app.services.visit_store import add_visit, _store
from app.models.domain_visit import DomainVisit


@pytest.fixture(autouse=True)
def reset_store():
    _store.clear()
    yield
    _store.clear()


def make_closed_visit(user_id, domain, start, duration_minutes=5):
    v = DomainVisit(user_id=user_id, domain=domain, start_time=start)
    end = start + timedelta(minutes=duration_minutes)
    v.close(end)
    add_visit(v)
    return v


NOW = datetime(2024, 6, 1, 10, 0, 0)


def test_compute_clusters_empty_returns_empty():
    result = compute_clusters("u1")
    assert result == []


def test_compute_clusters_single_visit_no_cluster():
    make_closed_visit("u1", "a.com", NOW)
    result = compute_clusters("u1")
    # single visit has no co-visit pair
    assert result == []


def test_compute_clusters_two_domains_in_same_session():
    make_closed_visit("u1", "a.com", NOW)
    make_closed_visit("u1", "b.com", NOW + timedelta(minutes=5))
    clusters = compute_clusters("u1")
    assert len(clusters) == 1
    assert set(clusters[0].domains) == {"a.com", "b.com"}
    assert clusters[0].co_visit_count == 1


def test_compute_clusters_domains_in_different_sessions_not_clustered():
    make_closed_visit("u1", "a.com", NOW)
    make_closed_visit("u1", "b.com", NOW + timedelta(hours=2))
    clusters = compute_clusters("u1")
    assert clusters == []


def test_compute_clusters_repeated_co_visits_increase_count():
    for i in range(3):
        base = NOW + timedelta(hours=i * 3)
        make_closed_visit("u1", "a.com", base)
        make_closed_visit("u1", "b.com", base + timedelta(minutes=5))
    clusters = compute_clusters("u1")
    assert len(clusters) == 1
    assert clusters[0].co_visit_count == 3


def test_compute_clusters_isolates_users():
    make_closed_visit("u1", "a.com", NOW)
    make_closed_visit("u1", "b.com", NOW + timedelta(minutes=5))
    make_closed_visit("u2", "x.com", NOW)
    make_closed_visit("u2", "y.com", NOW + timedelta(minutes=5))
    u1_clusters = compute_clusters("u1")
    u2_clusters = compute_clusters("u2")
    assert all("x.com" not in c.domains for c in u1_clusters)
    assert all("a.com" not in c.domains for c in u2_clusters)


def test_get_cluster_for_domain_returns_correct_cluster():
    make_closed_visit("u1", "a.com", NOW)
    make_closed_visit("u1", "b.com", NOW + timedelta(minutes=5))
    cluster = get_cluster_for_domain("u1", "a.com")
    assert cluster is not None
    assert "b.com" in cluster.domains


def test_get_cluster_for_domain_unknown_returns_none():
    result = get_cluster_for_domain("u1", "unknown.com")
    assert result is None


def test_split_into_sessions_respects_gap():
    base = NOW
    visits = [
        DomainVisit(user_id="u", domain="a.com", start_time=base),
        DomainVisit(user_id="u", domain="b.com", start_time=base + timedelta(minutes=10)),
        DomainVisit(user_id="u", domain="c.com", start_time=base + timedelta(hours=2)),
    ]
    for v in visits:
        v.close(v.start_time + timedelta(minutes=2))
    sessions = _split_into_sessions(visits)
    assert len(sessions) == 2
