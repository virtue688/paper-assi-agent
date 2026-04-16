from __future__ import annotations


class TaskPlanner:
    PLANS = {
        "daily_monitor": ["search", "dedup", "summarize", "extract_architecture", "report"],
        "paper_search": ["search", "summarize", "extract_architecture", "report"],
        "review_generation": ["search", "aggregate", "classify", "build_review", "export"],
        "paper_compare": ["fetch", "summarize", "compare", "report"],
        "trend_analysis": ["search", "cluster", "trend_analysis", "report"],
    }

    def plan(self, intent: str) -> list[str]:
        return list(self.PLANS.get(intent, self.PLANS["paper_search"]))
