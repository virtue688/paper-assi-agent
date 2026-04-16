from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paper_agent import PaperAssistantAgent
from agent.scheduler import DailyMonitorScheduler


if __name__ == "__main__":
    agent = PaperAssistantAgent(skill_dir="skills")
    scheduler = DailyMonitorScheduler(agent)
    result = scheduler.run_once(
        [
            "open-vocabulary detection",
            "vision-language navigation",
            "multimodal segmentation",
        ]
    )
    print(result.message)
    print(result.artifacts)
