from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

VALID_MOODS = {"great", "good", "neutral", "bad", "terrible"}


@dataclass
class DomainMood:
    user_id: str
    domain: str
    mood: str
    note: Optional[str] = None
    mood_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recorded_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.mood not in VALID_MOODS:
            raise ValueError(f"mood must be one of {VALID_MOODS}, got '{self.mood}'")

    def update(self, mood: Optional[str] = None, note: Optional[str] = None) -> None:
        if mood is not None:
            if mood not in VALID_MOODS:
                raise ValueError(f"mood must be one of {VALID_MOODS}, got '{mood}'")
            self.mood = mood
        if note is not None:
            self.note = note
        self.recorded_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "mood_id": self.mood_id,
            "user_id": self.user_id,
            "domain": self.domain,
            "mood": self.mood,
            "note": self.note,
            "recorded_at": self.recorded_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict) -> "DomainMood":
        return DomainMood(
            mood_id=data["mood_id"],
            user_id=data["user_id"],
            domain=data["domain"],
            mood=data["mood"],
            note=data.get("note"),
            recorded_at=datetime.fromisoformat(data["recorded_at"]),
        )
