from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Bookmark:
    user_id: str
    domain: str
    url: str
    title: str
    bookmark_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    note: str = ""
    tags: list = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    pinned: bool = False

    def update_title(self, new_title: str) -> None:
        if not new_title or not new_title.strip():
            raise ValueError("title cannot be blank")
        self.title = new_title.strip()

    def toggle_pin(self) -> bool:
        self.pinned = not self.pinned
        return self.pinned

    def to_dict(self) -> dict:
        return {
            "bookmark_id": self.bookmark_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "url": self.url,
            "title": self.title,
            "note": self.note,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "pinned": self.pinned,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            user_id=data["user_id"],
            domain=data["domain"],
            url=data["url"],
            title=data["title"],
            bookmark_id=data.get("bookmark_id", str(uuid.uuid4())),
            note=data.get("note", ""),
            tags=data.get("tags", []),
            created_at=created_at or datetime.now(timezone.utc),
            pinned=data.get("pinned", False),
        )
