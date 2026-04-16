from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paper_agent import PaperAssistantAgent


if __name__ == "__main__":
    agent = PaperAssistantAgent(skill_dir="skills")
    result = agent.run(
        {
            "intent": "paper_search",
            "keyword": "open-vocabulary object detection",
            "years": 3,
            "top_k": 5,
        }
    )
    print(result.message)
    print(result.artifacts)
