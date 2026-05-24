from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class VisitLimit:
    user_id: str
    domain: str
    max_visits_per_day: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True

    def __post_init__(self):
        if self.max_visits_per_day < 1:
            raise ValueError("max_visits_per_day must be at least 1")

    def is_exceeded(self, visit_count: int) -> bool:
        return self.enabled and visit_count >= self.max_visits_per_day

    def percent_used(self, visit_count: int) -> float:
        if self.max_visits_per_day == 0:
            return 100.0
        return round((visit_count / self.max_visits_per_day) * 100, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "max_visits_per_day": self.max_visits_per_day,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def from_dict(d: dict) -> "VisitLimit":
        return VisitLimit(
            id=d["id"],
            user_id=d["user_id"],
            domain=d["domain"],
            max_visits_per_day=d["max_visits_per_day"],
            enabled=d.get("enabled", True),
            created_at=datetime.fromisoformat(d["created_at"]),
        )
