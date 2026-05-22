from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class ExportRecord:
    user_id: str
    domain: str
    start_time: str
    end_time: str
    duration_seconds: float
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "tags": self.tags,
        }


@dataclass
class ExportBundle:
    user_id: str
    generated_at: str
    records: List[ExportRecord] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "generated_at": self.generated_at,
            "record_count": len(self.records),
            "records": [r.to_dict() for r in self.records],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ExportBundle":
        records = [
            ExportRecord(**r) for r in data.get("records", [])
        ]
        return ExportBundle(
            user_id=data["user_id"],
            generated_at=data["generated_at"],
            records=records,
        )
