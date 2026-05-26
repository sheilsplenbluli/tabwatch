from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class DomainFlag:
    user_id: str
    domain: str
    reason: str
    flag_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    notes: str = ""

    def __post_init__(self):
        if not self.reason.strip():
            raise ValueError("reason must not be blank")
        if not self.domain.strip():
            raise ValueError("domain must not be blank")

    def resolve(self, notes: str = "") -> None:
        if self.resolved:
            return
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.notes = notes

    def is_resolved(self) -> bool:
        return self.resolved

    def to_dict(self) -> dict:
        return {
            "flag_id": self.flag_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: dict) -> "DomainFlag":
        f = DomainFlag(
            user_id=data["user_id"],
            domain=data["domain"],
            reason=data["reason"],
            flag_id=data["flag_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            resolved=data.get("resolved", False),
            notes=data.get("notes", ""),
        )
        if data.get("resolved_at"):
            f.resolved_at = datetime.fromisoformat(data["resolved_at"])
        return f
