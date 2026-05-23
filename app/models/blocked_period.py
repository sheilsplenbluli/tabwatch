from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional
import uuid


@dataclass
class BlockedPeriod:
    user_id: str
    label: str
    start_time: str  # "HH:MM" 24h format
    end_time: str    # "HH:MM" 24h format
    days: list[str]  # e.g. ["mon", "tue", "wed"]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    active: bool = True

    VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}

    def is_active_now(self, now: Optional[datetime] = None) -> bool:
        if not self.active:
            return False
        now = now or datetime.utcnow()
        day_abbr = now.strftime("%a").lower()
        if day_abbr not in self.days:
            return False
        current = now.time().replace(second=0, microsecond=0)
        start = time(*map(int, self.start_time.split(":")))
        end = time(*map(int, self.end_time.split(":")))
        if start <= end:
            return start <= current <= end
        # overnight span
        return current >= start or current <= end

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "label": self.label,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "days": self.days,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BlockedPeriod":
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            label=data["label"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            days=data["days"],
            active=data.get("active", True),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
