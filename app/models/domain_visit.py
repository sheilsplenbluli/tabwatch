from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DomainVisit:
    """
    Represents a single domain visit session tracked by the browser extension.
    """
    domain: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int = 0
    id: Optional[int] = None

    def close(self, end_time: Optional[datetime] = None) -> None:
        """Mark the visit as ended and calculate duration."""
        self.end_time = end_time or datetime.utcnow()
        if self.start_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = max(0, int(delta.total_seconds()))

    @property
    def is_active(self) -> bool:
        """Return True if the visit session is still open."""
        return self.end_time is None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "domain": self.domain,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DomainVisit":
        return cls(
            id=data.get("id"),
            domain=data["domain"],
            user_id=data["user_id"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            duration_seconds=data.get("duration_seconds", 0),
        )

    def effective_duration(self) -> int:
        """Return the current duration in seconds.

        For closed visits, returns the stored duration_seconds. For active
        visits, calculates the elapsed time from start_time to now so callers
        always get an up-to-date value without needing to close the visit first.
        """
        if not self.is_active:
            return self.duration_seconds
        delta = datetime.utcnow() - self.start_time
        return max(0, int(delta.total_seconds()))
