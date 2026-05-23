from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class WhitelistEntry:
    user_id: str
    domain: str
    label: Optional[str] = None
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "label": self.label,
            "added_at": self.added_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WhitelistEntry":
        added_at = data.get("added_at")
        if isinstance(added_at, str):
            added_at = datetime.fromisoformat(added_at)
        return cls(
            user_id=data["user_id"],
            domain=data["domain"],
            label=data.get("label"),
            added_at=added_at or datetime.now(timezone.utc),
        )

    def matches(self, domain: str) -> bool:
        return self.domain.lower() == domain.lower()
