"""Groups domains into clusters based on co-visit patterns within sessions."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.services.visit_store import get_visits_for_user

_SESSION_GAP_MINUTES = 30


@dataclass
class DomainCluster:
    cluster_id: str
    user_id: str
    domains: List[str] = field(default_factory=list)
    co_visit_count: int = 0

    def to_dict(self) -> dict:
        return {
            "cluster_id": self.cluster_id,
            "user_id": self.user_id,
            "domains": self.domains,
            "co_visit_count": self.co_visit_count,
        }


def _closed_visits_sorted(user_id: str):
    visits = get_visits_for_user(user_id)
    closed = [v for v in visits if not v.is_active()]
    return sorted(closed, key=lambda v: v.start_time)


def _split_into_sessions(visits, gap_minutes: int = _SESSION_GAP_MINUTES):
    """Split a sorted list of visits into sessions based on idle gap."""
    if not visits:
        return []
    sessions = []
    current = [visits[0]]
    for v in visits[1:]:
        prev_end = current[-1].end_time or current[-1].start_time
        if (v.start_time - prev_end) > timedelta(minutes=gap_minutes):
            sessions.append(current)
            current = [v]
        else:
            current.append(v)
    sessions.append(current)
    return sessions


def compute_clusters(user_id: str) -> List[DomainCluster]:
    """Return domain clusters derived from co-visit sessions."""
    visits = _closed_visits_sorted(user_id)
    sessions = _split_into_sessions(visits)

    pair_counts: Dict[tuple, int] = {}
    for session in sessions:
        domains = list(dict.fromkeys(v.domain for v in session))
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                key = tuple(sorted([domains[i], domains[j]]))
                pair_counts[key] = pair_counts.get(key, 0) + 1

    # Build clusters: merge pairs that share a domain
    clusters: List[set] = []
    counts: Dict[int, int] = {}
    for (d1, d2), cnt in pair_counts.items():
        merged = False
        for idx, cluster in enumerate(clusters):
            if d1 in cluster or d2 in cluster:
                cluster.update([d1, d2])
                counts[idx] = counts.get(idx, 0) + cnt
                merged = True
                break
        if not merged:
            clusters.append({d1, d2})
            counts[len(clusters) - 1] = cnt

    result = []
    for idx, domain_set in enumerate(clusters):
        result.append(DomainCluster(
            cluster_id=f"{user_id}-cluster-{idx}",
            user_id=user_id,
            domains=sorted(domain_set),
            co_visit_count=counts.get(idx, 0),
        ))
    return sorted(result, key=lambda c: c.co_visit_count, reverse=True)


def get_cluster_for_domain(user_id: str, domain: str) -> Optional[DomainCluster]:
    """Return the cluster containing the given domain, if any."""
    for cluster in compute_clusters(user_id):
        if domain in cluster.domains:
            return cluster
    return None
