from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from app.services.visit_store import get_all_visits
from app.services.tag_tagger import get_tags_for_domain
from app.services.domain_insights import get_domain_insight


@dataclass
class DomainSearchResult:
    domain: str
    total_visits: int
    total_minutes: float
    tags: List[str]

    def to_dict(self) -> dict:
        return {
            "domain": self.domain,
            "total_visits": self.total_visits,
            "total_minutes": round(self.total_minutes, 2),
            "tags": self.tags,
        }


def _all_domains_for_user(user_id: str) -> List[str]:
    visits = get_all_visits(user_id)
    seen = set()
    domains = []
    for v in visits:
        if v.domain not in seen:
            seen.add(v.domain)
            domains.append(v.domain)
    return domains


def search_domains(
    user_id: str,
    query: str,
    tag_filter: Optional[str] = None,
    min_minutes: float = 0.0,
    limit: int = 20,
) -> List[DomainSearchResult]:
    """Search domains visited by a user with optional filters."""
    query = query.strip().lower()
    domains = _all_domains_for_user(user_id)
    results = []

    for domain in domains:
        if query and query not in domain.lower():
            continue

        insight = get_domain_insight(user_id, domain)
        if insight is None:
            continue

        total_minutes = insight.total_seconds / 60.0
        if total_minutes < min_minutes:
            continue

        tags = [t.name for t in get_tags_for_domain(user_id, domain)]
        if tag_filter and tag_filter not in tags:
            continue

        results.append(
            DomainSearchResult(
                domain=domain,
                total_visits=insight.visit_count,
                total_minutes=total_minutes,
                tags=tags,
            )
        )

    results.sort(key=lambda r: r.total_minutes, reverse=True)
    return results[:limit]
