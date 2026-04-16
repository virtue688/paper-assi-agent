from __future__ import annotations

import argparse
import json

from agent.paper_agent import PaperAssistantAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Paper Agent command line entrypoint")
    parser.add_argument("--intent", default="paper_search", choices=["daily_monitor", "paper_search", "review_generation", "paper_compare", "trend_analysis"])
    parser.add_argument("--keyword", default="open-vocabulary object detection")
    parser.add_argument("--years", type=int, default=3)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    agent = PaperAssistantAgent(skill_dir="skills")
    result = agent.run({"intent": args.intent, "keyword": args.keyword, "years": args.years, "top_k": args.top_k})
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
