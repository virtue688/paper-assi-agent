from agent.router import IntentRouter


def test_router_explicit_intent():
    assert IntentRouter().route({"intent": "review_generation"}) == "review_generation"


def test_router_infers_compare():
    assert IntentRouter().route({"query": "请对比这几篇论文"}) == "paper_compare"
