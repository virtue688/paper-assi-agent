from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agent.paper_agent import PaperAssistantAgent


if __name__ == "__main__":
    agent = PaperAssistantAgent(skill_dir="skills")
    result = agent.run(
        {
            "intent": "paper_compare",
            "papers": [
                {
                    "title": "CLIP for Open-Vocabulary Recognition",
                    "abstract": "A vision-language model aligns image and text representations for zero-shot recognition.",
                    "url": "https://example.com/clip",
                    "authors": ["Demo Author"],
                    "year": 2021,
                    "source": "demo",
                },
                {
                    "title": "Diffusion Policy for Robot Control",
                    "abstract": "A diffusion model predicts action trajectories for imitation learning and robotic policy learning.",
                    "url": "https://example.com/diffusion-policy",
                    "authors": ["Demo Author"],
                    "year": 2023,
                    "source": "demo",
                },
            ],
        }
    )
    print(result.message)
    print(result.artifacts)
