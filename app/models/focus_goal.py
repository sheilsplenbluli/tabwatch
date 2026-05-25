from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class FocusGoal:
    user_id: str
    label: str
    target_minutes: int
    domains: list = field(default_factory=list)
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        if self.target_minutes <= 0:
            raise ValueError("target_minutes must be positive")
        if not self.label or not self.label.strip():
            raise ValueError("label must not be blank")

    def complete(self, at: Optional[datetime] = None) -> None:
        if self.completed_at is None:
            self.completed_at = at or datetime.utcnow()
            self.is_active = False

    def is_completed(self) -> bool:
        return self.completed_at is not None

    def to_dict(self) -> dict:
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "label": self.label,
            "target_minutes": self.target_minutes,
            "domains": list(self.domains),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FocusGoal":
        obj = cls(
            user_id=data["user_id"],
            label=data["label"],
            target_minutes=data["target_minutes"],
            domains=data.get("domains", []),
            goal_id=data["goal_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            is_active=data.get("is_active", True),
        )
        if data.get("completed_at"):
            obj.completed_at = datetime.fromisoformat(data["completed_at"])
        return obj
