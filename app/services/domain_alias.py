"""Map user-defined aliases to canonical domains.

Allows users to treat e.g. 'mail.google.com' and 'gmail.com'
as the same domain for reporting purposes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid

# { alias_id -> DomainAlias }
_store: Dict[str, "DomainAlias"] = {}


@dataclass
class DomainAlias:
    user_id: str
    canonical: str          # the "true" domain name
    aliases: List[str] = field(default_factory=list)
    alias_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_alias(self, domain: str) -> None:
        if domain not in self.aliases:
            self.aliases.append(domain)

    def remove_alias(self, domain: str) -> None:
        self.aliases = [a for a in self.aliases if a != domain]

    def resolves(self, domain: str) -> bool:
        """Return True if *domain* is the canonical name or a known alias."""
        return domain == self.canonical or domain in self.aliases

    def to_dict(self) -> dict:
        return {
            "alias_id": self.alias_id,
            "user_id": self.user_id,
            "canonical": self.canonical,
            "aliases": list(self.aliases),
        }

    @staticmethod
    def from_dict(data: dict) -> "DomainAlias":
        obj = DomainAlias(
            user_id=data["user_id"],
            canonical=data["canonical"],
            aliases=list(data.get("aliases", [])),
            alias_id=data["alias_id"],
        )
        return obj


# ---------------------------------------------------------------------------
# Store helpers
# ---------------------------------------------------------------------------

def create_alias(user_id: str, canonical: str, aliases: Optional[List[str]] = None) -> DomainAlias:
    entry = DomainAlias(user_id=user_id, canonical=canonical, aliases=list(aliases or []))
    _store[entry.alias_id] = entry
    return entry


def get_alias(alias_id: str) -> Optional[DomainAlias]:
    return _store.get(alias_id)


def get_aliases_for_user(user_id: str) -> List[DomainAlias]:
    return [a for a in _store.values() if a.user_id == user_id]


def delete_alias(alias_id: str) -> bool:
    if alias_id in _store:
        del _store[alias_id]
        return True
    return False


def resolve_domain(user_id: str, domain: str) -> str:
    """Return the canonical domain for *domain*, or *domain* itself if not aliased."""
    for entry in get_aliases_for_user(user_id):
        if entry.resolves(domain):
            return entry.canonical
    return domain


def clear_all() -> None:
    _store.clear()
