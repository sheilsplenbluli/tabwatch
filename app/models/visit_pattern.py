from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HourlyPattern:
    hour: int  # 0-23
    visit_count: int = 0
    total_minutes: float = 0.0

    def to_dict(self) -> dict:
        return {
            "hour": self.hour,
            "visit_count": self.visit_count,
            "total_minutes": round(self.total_minutes, 2),
        }


@dataclass
class VisitPattern:
    user_id: str
    domain: str
    hourly: List[HourlyPattern] = field(default_factory=lambda: [HourlyPattern(h) for h in range(24)])
    peak_hour: Optional[int] = None
    avg_session_minutes: float = 0.0
    total_visits: int = 0

    def compute_peak(self) -> Optional[int]:
        if not any(h.visit_count for h in self.hourly):
            return None
        return max(self.hourly, key=lambda h: h.visit_count).hour

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "hourly": [h.to_dict() for h in self.hourly],
            "peak_hour": self.peak_hour,
            "avg_session_minutes": round(self.avg_session_minutes, 2),
            "total_visits": self.total_visits,
        }
