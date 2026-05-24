from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class TabSnapshot:
    user_id: str
    domains: List[str]
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    restored_at: Optional[datetime] = None
    tab_count: int = 0

    def __post_init__(self):
        self.tab_count = len(self.domains)

    def restore(self) -> None:
        """Mark snapshot as restored."""
        if self.restored_at is None:
            self.restored_at = datetime.utcnow()

    def is_restored(self) -> bool:
        return self.restored_at is not None

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "user_id": self.user_id,
            "domains": self.domains,
            "label": self.label,
            "tab_count": self.tab_count,
            "created_at": self.created_at.isoformat(),
            "restored_at": self.restored_at.isoformat() if self.restored_at else None,
            "is_restored": self.is_restored(),
        }

    @staticmethod
    def from_dict(data: dict) -> "TabSnapshot":
        snap = TabSnapshot(
            user_id=data["user_id"],
            domains=data["domains"],
            snapshot_id=data.get("snapshot_id", str(uuid.uuid4())),
            label=data.get("label"),
            created_at=datetime.fromisoformat(data["created_at"]),
            restored_at=datetime.fromisoformat(data["restored_at"]) if data.get("restored_at") else None,
        )
        snap.tab_count = len(snap.domains)
        return snap
