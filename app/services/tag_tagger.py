"""Auto-tag visits based on existing tag rules for a user."""

from typing import List
from app.models.domain_visit import DomainVisit
from app.services.tag_store import get_tags_for_user


def get_tags_for_domain(user_id: str, domain: str) -> List[str]:
    """Return tag names that match the given domain for a user."""
    tags = get_tags_for_user(user_id)
    matched = []
    for tag in tags:
        if tag.matches_domain(domain):
            matched.append(tag.name)
    return matched


def annotate_visit(user_id: str, visit: DomainVisit) -> DomainVisit:
    """Attach matching tag names to a visit's metadata dict.

    The visit object is mutated in-place and also returned for convenience.
    """
    tags = get_tags_for_domain(user_id, visit.domain)
    if not hasattr(visit, "tags") or visit.tags is None:
        visit.tags = []
    for tag in tags:
        if tag not in visit.tags:
            visit.tags.append(tag)
    return visit


def annotate_visits(user_id: str, visits: List[DomainVisit]) -> List[DomainVisit]:
    """Annotate a list of visits with matching tags."""
    return [annotate_visit(user_id, v) for v in visits]


def visits_for_tag(user_id: str, tag_name: str, visits: List[DomainVisit]) -> List[DomainVisit]:
    """Filter visits to only those whose domain matches the named tag."""
    tag_list = get_tags_for_user(user_id)
    target = next((t for t in tag_list if t.name == tag_name), None)
    if target is None:
        return []
    return [v for v in visits if target.matches_domain(v.domain)]
