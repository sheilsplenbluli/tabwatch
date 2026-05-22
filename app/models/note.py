from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Note:
    user_id: str
    domain: str
    body: str
    note_id: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at

    def update_body(self, new_body: str) -> None:
        self.body = new_body
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "note_id": self.note_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "body": self.body,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        note = cls(
            user_id=data["user_id"],
            domain=data["domain"],
            body=data["body"],
            note_id=data.get("note_id", ""),
        )
        if data.get("created_at"):
            note.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            note.updated_at = datetime.fromisoformat(data["updated_at"])
        return note
