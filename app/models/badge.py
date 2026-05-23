from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Badge:
    badge_id: str
    user_id: str
    name: str
    description: str
    icon: str
    earned_at: Optional[datetime] = None
    seen: bool = False

    def earn(self, at: Optional[datetime] = None) -> None:
        """Mark this badge as earned."""
        if self.earned_at is not None:
            return  # already earned, idempotent
        self.earned_at = at or datetime.utcnow()

    def is_earned(self) -> bool:
        return self.earned_at is not None

    def mark_seen(self) -> None:
        self.seen = True

    def to_dict(self) -> dict:
        return {
            "badge_id": self.badge_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "earned_at": self.earned_at.isoformat() if self.earned_at else None,
            "seen": self.seen,
        }

    @staticmethod
    def from_dict(data: dict) -> "Badge":
        earned_at = data.get("earned_at")
        return Badge(
            badge_id=data["badge_id"],
            user_id=data["user_id"],
            name=data["name"],
            description=data["description"],
            icon=data["icon"],
            earned_at=datetime.fromisoformat(earned_at) if earned_at else None,
            seen=data.get("seen", False),
        )
