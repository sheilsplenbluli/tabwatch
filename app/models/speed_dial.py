from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class SpeedDial:
    user_id: str
    domain: str
    label: str
    position: int = 0
    pinned: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_visited_at: Optional[str] = None

    def update_label(self, new_label: str) -> None:
        stripped = new_label.strip()
        if not stripped:
            raise ValueError("Label cannot be blank")
        self.label = stripped

    def move_to(self, position: int) -> None:
        if position < 0:
            raise ValueError("Position cannot be negative")
        self.position = position

    def toggle_pin(self) -> None:
        self.pinned = not self.pinned

    def touch(self) -> None:
        self.last_visited_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "label": self.label,
            "position": self.position,
            "pinned": self.pinned,
            "created_at": self.created_at,
            "last_visited_at": self.last_visited_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SpeedDial":
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            domain=data["domain"],
            label=data["label"],
            position=data.get("position", 0),
            pinned=data.get("pinned", False),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            last_visited_at=data.get("last_visited_at"),
        )
