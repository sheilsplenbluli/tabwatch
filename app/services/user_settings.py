"""User settings management for digest preferences and notification config."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserSettings:
    user_id: str
    email: str
    digest_enabled: bool = True
    digest_day: str = "monday"  # day of week to send digest
    digest_hour: int = 8         # hour in UTC (0-23)
    top_domains_limit: int = 10
    timezone: str = "UTC"
    unsubscribed: bool = False

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "digest_enabled": self.digest_enabled,
            "digest_day": self.digest_day,
            "digest_hour": self.digest_hour,
            "top_domains_limit": self.top_domains_limit,
            "timezone": self.timezone,
            "unsubscribed": self.unsubscribed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        return cls(
            user_id=data["user_id"],
            email=data["email"],
            digest_enabled=data.get("digest_enabled", True),
            digest_day=data.get("digest_day", "monday"),
            digest_hour=data.get("digest_hour", 8),
            top_domains_limit=data.get("top_domains_limit", 10),
            timezone=data.get("timezone", "UTC"),
            unsubscribed=data.get("unsubscribed", False),
        )

    def is_eligible_for_digest(self) -> bool:
        """Return True if user should receive digest emails."""
        return self.digest_enabled and not self.unsubscribed and bool(self.email)


# In-memory store; replace with DB-backed store in production
_settings_store: dict[str, UserSettings] = {}


def get_user_settings(user_id: str) -> Optional[UserSettings]:
    return _settings_store.get(user_id)


def save_user_settings(settings: UserSettings) -> None:
    _settings_store[settings.user_id] = settings


def delete_user_settings(user_id: str) -> bool:
    if user_id in _settings_store:
        del _settings_store[user_id]
        return True
    return False
