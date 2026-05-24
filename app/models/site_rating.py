from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

VALID_RATINGS = {1, 2, 3, 4, 5}


@dataclass
class SiteRating:
    user_id: str
    domain: str
    rating: int  # 1-5
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.rating not in VALID_RATINGS:
            raise ValueError(f"rating must be one of {VALID_RATINGS}, got {self.rating}")

    def update(self, rating: Optional[int] = None, note: Optional[str] = None):
        if rating is not None:
            if rating not in VALID_RATINGS:
                raise ValueError(f"rating must be one of {VALID_RATINGS}, got {rating}")
            self.rating = rating
        if note is not None:
            self.note = note
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "domain": self.domain,
            "rating": self.rating,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SiteRating":
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            domain=data["domain"],
            rating=data["rating"],
            note=data.get("note", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
