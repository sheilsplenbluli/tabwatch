from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Reminder:
    user_id: str
    domain: str
    message: str
    remind_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    triggered: bool = False
    triggered_at: Optional[datetime] = None

    def trigger(self) -> None:
        """Mark this reminder as triggered."""
        if not self.triggered:
            self.triggered = True
            self.triggered_at = datetime.utcnow()

    def is_due(self, now: Optional[datetime] = None) -> bool:
        """Return True if the reminder is due and not yet triggered."""
        now = now or datetime.utcnow()
        return not self.triggered and self.remind_at <= now

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "message": self.message,
            "remind_at": self.remind_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "triggered": self.triggered,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Reminder":
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            domain=data["domain"],
            message=data["message"],
            remind_at=datetime.fromisoformat(data["remind_at"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            triggered=data.get("triggered", False),
            triggered_at=datetime.fromisoformat(data["triggered_at"]) if data.get("triggered_at") else None,
        )
