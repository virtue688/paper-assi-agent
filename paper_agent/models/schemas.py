from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Paper:
    title: str
    abstract: str = ""
    url: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str = ""
    source: str = ""
    paper_id: str = ""
    pdf_url: str = ""
    published_at: str = ""
    summary: str = ""
    highlights: list[str] = field(default_factory=list)
    method_tags: list[str] = field(default_factory=list)
    architecture_image_path: str = ""
    architecture_text: str = ""

    @property
    def dedup_key(self) -> str:
        return (self.paper_id or " ".join(self.title.lower().split())).lower().strip()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Paper":
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class CompareItem:
    title: str
    task: str
    innovation: str
    architecture: str
    experiments: str
    strengths: str
    limitations: str
    best_for: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewReport:
    title: str
    background: str
    problem_definition: str
    technical_routes: dict[str, list[str]]
    representative_methods: list[str]
    datasets_and_metrics: list[str]
    challenges: list[str]
    future_directions: list[str]
    references: list[dict[str, Any]]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentResult:
    intent: str
    status: str
    data: Any
    message: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if hasattr(self.data, "to_dict"):
            payload["data"] = self.data.to_dict()
        elif isinstance(self.data, list):
            payload["data"] = [item.to_dict() if hasattr(item, "to_dict") else item for item in self.data]
        return payload
