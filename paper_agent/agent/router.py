from __future__ import annotations

from typing import Any


class IntentRouter:
    SUPPORTED = {"daily_monitor", "paper_search", "review_generation", "paper_compare", "trend_analysis"}

    def route(self, task: dict[str, Any]) -> str:
        intent = task.get("intent")
        if intent in self.SUPPORTED:
            return intent
        text = " ".join(str(value).lower() for value in task.values())
        if "compare" in text or "对比" in text:
            return "paper_compare"
        if "trend" in text or "趋势" in text:
            return "trend_analysis"
        if "review" in text or "综述" in text:
            return "review_generation"
        if "monitor" in text or "daily" in text or "监控" in text:
            return "daily_monitor"
        return "paper_search"
