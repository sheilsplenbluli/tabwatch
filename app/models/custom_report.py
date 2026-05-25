from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class CustomReport:
    user_id: str
    name: str
    domains: List[str]
    start_iso: str
    end_iso: str
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    description: Optional[str] = None

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("Report name must not be blank")
        if not self.domains:
            raise ValueError("At least one domain is required")

    def update_name(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise ValueError("Report name must not be blank")
        self.name = new_name.strip()

    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "user_id": self.user_id,
            "name": self.name,
            "domains": self.domains,
            "start_iso": self.start_iso,
            "end_iso": self.end_iso,
            "description": self.description,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "CustomReport":
        r = CustomReport(
            user_id=data["user_id"],
            name=data["name"],
            domains=data["domains"],
            start_iso=data["start_iso"],
            end_iso=data["end_iso"],
            description=data.get("description"),
        )
        r.report_id = data["report_id"]
        r.created_at = data["created_at"]
        return r
