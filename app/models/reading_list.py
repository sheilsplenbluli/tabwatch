from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class ReadingListEntry:
    user_id: str
    url: str
    domain: str
    title: str
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None
    archived: bool = False
    notes: str = ""

    def mark_read(self, when: Optional[datetime] = None) -> None:
        if self.read_at is None:
            self.read_at = when or datetime.now(timezone.utc)

    def archive(self) -> None:
        self.archived = True

    def is_read(self) -> bool:
        return self.read_at is not None

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "url": self.url,
            "domain": self.domain,
            "title": self.title,
            "added_at": self.added_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "archived": self.archived,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "ReadingListEntry":
        entry = ReadingListEntry(
            user_id=data["user_id"],
            url=data["url"],
            domain=data["domain"],
            title=data["title"],
            entry_id=data.get("entry_id", str(uuid.uuid4())),
            notes=data.get("notes", ""),
            archived=data.get("archived", False),
        )
        if data.get("added_at"):
            entry.added_at = datetime.fromisoformat(data["added_at"])
        if data.get("read_at"):
            entry.read_at = datetime.fromisoformat(data["read_at"])
        return entry
