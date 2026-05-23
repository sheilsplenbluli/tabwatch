from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class TimeBudget:
    user_id: str
    domain: str
    daily_limit_minutes: int
    budget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: Optional[str] = None
    enabled: bool = True

    def is_exceeded(self, minutes_used: float) -> bool:
        return self.enabled and minutes_used >= self.daily_limit_minutes

    def percent_used(self, minutes_used: float) -> float:
        if self.daily_limit_minutes <= 0:
            return 100.0
        return round((minutes_used / self.daily_limit_minutes) * 100, 1)

    def to_dict(self) -> dict:
        return {
            "budget_id": self.budget_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "daily_limit_minutes": self.daily_limit_minutes,
            "label": self.label,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TimeBudget":
        return cls(
            budget_id=data["budget_id"],
            user_id=data["user_id"],
            domain=data["domain"],
            daily_limit_minutes=data["daily_limit_minutes"],
            label=data.get("label"),
            enabled=data.get("enabled", True),
        )
