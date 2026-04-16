from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from models.schemas import Paper


class StorageTool:
    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.cache_dir = self.base_dir / "cache"
        self.paper_dir = self.base_dir / "papers"
        self.report_dir = self.base_dir / "reports"
        for path in [self.cache_dir, self.paper_dir, self.report_dir]:
            path.mkdir(parents=True, exist_ok=True)
        self.seen_path = self.cache_dir / "seen_papers.json"
        self.subscriptions_path = self.cache_dir / "subscriptions.json"
        self.history_path = self.cache_dir / "history.json"

    def load_json(self, path: Path, default: Any) -> Any:
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default

    def save_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_seen_keys(self) -> set[str]:
        return set(self.load_json(self.seen_path, []))

    def mark_seen(self, papers: list[Paper]) -> None:
        keys = self.get_seen_keys()
        keys.update(paper.dedup_key for paper in papers if paper.title)
        self.save_json(self.seen_path, sorted(keys))

    def filter_new(self, papers: list[Paper]) -> list[Paper]:
        seen = self.get_seen_keys()
        unique: dict[str, Paper] = {}
        for paper in papers:
            if paper.dedup_key and paper.dedup_key not in seen:
                unique.setdefault(paper.dedup_key, paper)
        return list(unique.values())

    def save_report(self, name: str, content: str, suffix: str = "md") -> str:
        safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name).strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.report_dir / f"{timestamp}_{safe_name}.{suffix}"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def save_result_json(self, name: str, payload: Any) -> str:
        safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name).strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.report_dir / f"{timestamp}_{safe_name}.json"
        self.save_json(path, payload)
        return str(path)

    def append_history(self, event: dict[str, Any]) -> None:
        history = self.load_json(self.history_path, [])
        history.append({"time": datetime.now().isoformat(), **event})
        self.save_json(self.history_path, history[-200:])

    def load_subscriptions(self) -> list[str]:
        return self.load_json(self.subscriptions_path, [])

    def save_subscriptions(self, keywords: list[str]) -> None:
        cleaned = sorted({item.strip() for item in keywords if item.strip()})
        self.save_json(self.subscriptions_path, cleaned)
