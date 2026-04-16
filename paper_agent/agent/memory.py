from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any

from models.schemas import Paper


@dataclass
class AgentMemory:
    current_task: dict[str, Any] = field(default_factory=dict)
    recent_actions: deque[str] = field(default_factory=lambda: deque(maxlen=30))
    recent_results: list[Paper] = field(default_factory=list)
    subscriptions: list[str] = field(default_factory=list)
    report_history: list[str] = field(default_factory=list)

    def set_task(self, task: dict[str, Any]) -> None:
        self.current_task = task

    def add_action(self, action: str) -> None:
        self.recent_actions.append(action)

    def set_results(self, papers: list[Paper]) -> None:
        self.recent_results = papers

    def add_report(self, path: str) -> None:
        self.report_history.append(path)
        self.report_history = self.report_history[-20:]

    def snapshot(self) -> dict[str, Any]:
        return {
            "current_task": self.current_task,
            "recent_actions": list(self.recent_actions),
            "recent_results": [paper.to_dict() for paper in self.recent_results],
            "subscriptions": self.subscriptions,
            "report_history": self.report_history,
        }
