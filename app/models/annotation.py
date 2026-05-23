from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Annotation:
    user_id: str
    domain: str
    body: str
    label: str = ""  # e.g. 'productive', 'distraction', 'research'
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    def update(self, body: str = None, label: str = None) -> None:
        if body is not None:
            if not body.strip():
                raise ValueError("Annotation body cannot be blank")
            self.body = body.strip()
        if label is not None:
            self.label = label.strip()
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "body": self.body,
            "label": self.label,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Annotation":
        obj = cls(
            user_id=data["user_id"],
            domain=data["domain"],
            body=data["body"],
            label=data.get("label", ""),
            id=data.get("id", str(uuid.uuid4())),
        )
        if data.get("created_at"):
            obj.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            obj.updated_at = datetime.fromisoformat(data["updated_at"])
        return obj
