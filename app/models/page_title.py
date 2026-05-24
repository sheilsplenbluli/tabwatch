from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class PageTitle:
    user_id: str
    domain: str
    url: str
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    visit_count: int = 1

    def touch(self, title: Optional[str] = None) -> None:
        """Update last_seen and optionally update the title."""
        self.last_seen = datetime.now(timezone.utc)
        self.visit_count += 1
        if title and title.strip():
            self.title = title.strip()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "url": self.url,
            "title": self.title,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "visit_count": self.visit_count,
        }

    @staticmethod
    def from_dict(data: dict) -> "PageTitle":
        return PageTitle(
            id=data["id"],
            user_id=data["user_id"],
            domain=data["domain"],
            url=data["url"],
            title=data["title"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_seen=datetime.fromisoformat(data["last_seen"]),
            visit_count=data.get("visit_count", 1),
        )
