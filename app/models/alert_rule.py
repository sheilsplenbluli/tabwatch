from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class AlertRule:
    """Defines a threshold alert for time spent on a domain."""
    user_id: str
    domain: str
    daily_limit_minutes: int
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = True
    notify_at_percent: int = 100  # e.g. 80 = warn at 80% of limit

    def is_triggered(self, minutes_spent: float) -> bool:
        """Return True if the spent time meets or exceeds the notify threshold."""
        if not self.enabled:
            return False
        threshold = self.daily_limit_minutes * (self.notify_at_percent / 100)
        return minutes_spent >= threshold

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "daily_limit_minutes": self.daily_limit_minutes,
            "enabled": self.enabled,
            "notify_at_percent": self.notify_at_percent,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AlertRule":
        return cls(
            rule_id=data.get("rule_id", str(uuid.uuid4())),
            user_id=data["user_id"],
            domain=data["domain"],
            daily_limit_minutes=data["daily_limit_minutes"],
            enabled=data.get("enabled", True),
            notify_at_percent=data.get("notify_at_percent", 100),
        )
