from dataclasses import dataclass, field
from typing import List, Optional
import uuid


@dataclass
class TabGroup:
    user_id: str
    name: str
    domains: List[str] = field(default_factory=list)
    color: Optional[str] = None
    group_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_domain(self, domain: str) -> None:
        if domain not in self.domains:
            self.domains.append(domain)

    def remove_domain(self, domain: str) -> None:
        self.domains = [d for d in self.domains if d != domain]

    def matches_domain(self, domain: str) -> bool:
        return domain in self.domains

    def rename(self, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("Tab group name cannot be blank")
        self.name = new_name

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "user_id": self.user_id,
            "name": self.name,
            "domains": list(self.domains),
            "color": self.color,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TabGroup":
        obj = cls(
            user_id=data["user_id"],
            name=data["name"],
            domains=list(data.get("domains", [])),
            color=data.get("color"),
        )
        obj.group_id = data.get("group_id", obj.group_id)
        return obj
