from agent.paper_agent import PaperAssistantAgent
from models.schemas import Paper


def test_agent_loads_skills():
    agent = PaperAssistantAgent(skill_dir="skills")
    assert "search_papers" in agent.skills


def test_agent_compare_demo_runs():
    agent = PaperAssistantAgent(skill_dir="skills")
    result = agent.run(
        {
            "intent": "paper_compare",
            "papers": [
                {
                    "title": "Open Vocabulary Detection",
                    "abstract": "Detect objects with language-guided open vocabulary labels.",
                    "year": 2024,
                }
            ],
        }
    )
    assert result.status == "ok"
    assert len(result.data) == 1
