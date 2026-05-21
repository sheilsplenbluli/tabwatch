from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Tag:
    tag_id: str
    user_id: str
    name: str
    domains: List[str] = field(default_factory=list)
    color: Optional[str] = None

    def add_domain(self, domain: str) -> None:
        if domain not in self.domains:
            self.domains.append(domain)

    def remove_domain(self, domain: str) -> None:
        self.domains = [d for d in self.domains if d != domain]

    def matches_domain(self, domain: str) -> bool:
        return domain in self.domains

    def to_dict(self) -> dict:
        return {
            "tag_id": self.tag_id,
            "user_id": self.user_id,
            "name": self.name,
            "domains": list(self.domains),
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        return cls(
            tag_id=data["tag_id"],
            user_id=data["user_id"],
            name=data["name"],
            domains=list(data.get("domains", [])),
            color=data.get("color"),
        )
