from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paper_agent import PaperAssistantAgent


if __name__ == "__main__":
    agent = PaperAssistantAgent(skill_dir="skills")
    result = agent.run(
        {
            "intent": "review_generation",
            "keyword": "visual grounding",
            "years": 5,
            "top_k": 8,
        }
    )
    print(result.message)
    print(result.artifacts)
