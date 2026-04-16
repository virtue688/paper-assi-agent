from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agent.memory import AgentMemory
from agent.planner import TaskPlanner
from agent.router import IntentRouter


class BaseAgent:
    def __init__(self, skill_dir: str = "skills", settings_path: str = "config/settings.yaml") -> None:
        self.skill_dir = Path(skill_dir)
        self.settings = self._load_yaml(settings_path)
        self.skills = self._load_skills()
        self.memory = AgentMemory()
        self.router = IntentRouter()
        self.planner = TaskPlanner()

    def _load_yaml(self, path: str) -> dict[str, Any]:
        file_path = Path(path)
        if not file_path.exists():
            return {}
        with file_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def _load_skills(self) -> dict[str, str]:
        skills: dict[str, str] = {}
        if not self.skill_dir.exists():
            return skills
        for path in sorted(self.skill_dir.glob("*.md")):
            skills[path.stem] = path.read_text(encoding="utf-8")
        return skills

    def run(self, task: dict[str, Any]):
        raise NotImplementedError
