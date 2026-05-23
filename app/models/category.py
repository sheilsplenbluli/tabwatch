from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Category:
    user_id: str
    name: str
    color: str = "#6366f1"
    domains: List[str] = field(default_factory=list)
    category_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_domain(self, domain: str) -> None:
        if domain not in self.domains:
            self.domains.append(domain)

    def remove_domain(self, domain: str) -> None:
        self.domains = [d for d in self.domains if d != domain]

    def matches_domain(self, domain: str) -> bool:
        return domain in self.domains

    def to_dict(self) -> dict:
        return {
            "category_id": self.category_id,
            "user_id": self.user_id,
            "name": self.name,
            "color": self.color,
            "domains": list(self.domains),
        }

    @staticmethod
    def from_dict(data: dict) -> "Category":
        c = Category(
            user_id=data["user_id"],
            name=data["name"],
            color=data.get("color", "#6366f1"),
            domains=list(data.get("domains", [])),
            category_id=data["category_id"],
        )
        return c
