from __future__ import annotations

from typing import Any

from agent.base_agent import BaseAgent
from models.schemas import AgentResult, Paper
from services import PaperService, ReportService, ReviewService
from tools import ArxivTool, FigureTool, OllamaLLM, PDFTool, SemanticScholarTool, StorageTool


class PaperAssistantAgent(BaseAgent):
    def __init__(self, skill_dir: str = "skills", settings_path: str = "config/settings.yaml") -> None:
        super().__init__(skill_dir=skill_dir, settings_path=settings_path)
        data_dir = self.settings.get("storage", {}).get("data_dir", "data")
        llm_cfg = self.settings.get("llm", {})
        semantic_cfg = self.settings.get("semantic_scholar", {})
        self.storage = StorageTool(base_dir=data_dir)
        self.llm = OllamaLLM(
            base_url=llm_cfg.get("base_url", "http://localhost:11434"),
            model=llm_cfg.get("model", "qwen3:3b"),
            timeout=llm_cfg.get("timeout", 60),
        )
        self.paper_service = PaperService(
            arxiv_tool=ArxivTool(),
            semantic_tool=SemanticScholarTool(api_key=semantic_cfg.get("api_key", "")),
            pdf_tool=PDFTool(paper_dir=f"{data_dir}/papers"),
            figure_tool=FigureTool(output_dir=f"{data_dir}/papers/figures"),
            llm=self.llm,
            storage=self.storage,
        )
        self.review_service = ReviewService(self.llm)
        self.report_service = ReportService(self.storage)
        self.memory.subscriptions = self.storage.load_subscriptions()

    def run(self, task: dict[str, Any]) -> AgentResult:
        self.memory.set_task(task)
        intent = self.router.route(task)
        plan = self.planner.plan(intent)
        self.memory.add_action(f"intent={intent}; plan={' -> '.join(plan)}")
        try:
            if intent == "daily_monitor":
                return self._daily_monitor(task)
            if intent == "paper_search":
                return self._paper_search(task)
            if intent == "review_generation":
                return self._review_generation(task)
            if intent == "paper_compare":
                return self._paper_compare(task)
            if intent == "trend_analysis":
                return self._trend_analysis(task)
        except Exception as exc:
            self.storage.append_history({"intent": intent, "status": "failed", "error": str(exc)})
            return AgentResult(intent=intent, status="failed", data={}, message=str(exc))
        return AgentResult(intent=intent, status="failed", data={}, message="Unsupported intent")

    def _daily_monitor(self, task: dict[str, Any]) -> AgentResult:
        keywords = task.get("keywords") or task.get("keyword") or self.memory.subscriptions
        if isinstance(keywords, str):
            keywords = [keywords]
        if keywords:
            self.storage.save_subscriptions(list(keywords))
            self.memory.subscriptions = list(keywords)
        top_k = int(task.get("top_k", self.settings.get("search", {}).get("top_k", 8)))
        papers = self.paper_service.search_many_keywords(keywords, years=task.get("years"), top_k=top_k)
        new_papers = self.paper_service.filter_new_and_mark(papers)
        enriched = self.paper_service.summarize_and_enrich(new_papers)
        self.memory.set_results(enriched)
        md = self.report_service.papers_to_markdown("Daily Paper Monitor", ", ".join(keywords), enriched)
        artifacts = self.report_service.export("daily_monitor", md, [paper.to_dict() for paper in enriched])
        self.memory.add_report(artifacts["markdown"])
        self.storage.append_history({"intent": "daily_monitor", "status": "ok", "papers": len(enriched)})
        return AgentResult("daily_monitor", "ok", enriched, f"Found {len(enriched)} new papers.", artifacts)

    def _paper_search(self, task: dict[str, Any]) -> AgentResult:
        keyword = task.get("keyword", "")
        papers = self.paper_service.search_papers(keyword, years=task.get("years"), top_k=int(task.get("top_k", 10)))
        enriched = self.paper_service.summarize_and_enrich(papers)
        self.memory.set_results(enriched)
        md = self.report_service.papers_to_markdown("Paper Search Report", keyword, enriched)
        artifacts = self.report_service.export("paper_search", md, [paper.to_dict() for paper in enriched])
        return AgentResult("paper_search", "ok", enriched, f"Returned {len(enriched)} papers.", artifacts)

    def _review_generation(self, task: dict[str, Any]) -> AgentResult:
        keyword = task.get("keyword", "")
        papers = self.paper_service.search_papers(keyword, years=task.get("years"), top_k=int(task.get("top_k", 10)))
        enriched = self.paper_service.summarize_and_enrich(papers, with_architecture=False)
        review = self.review_service.build_review(keyword, enriched)
        md = self.report_service.review_to_markdown(review)
        artifacts = self.report_service.export("review_generation", md, review)
        self.memory.set_results(enriched)
        self.memory.add_report(artifacts["markdown"])
        return AgentResult("review_generation", "ok", review, "Review generated.", artifacts)

    def _paper_compare(self, task: dict[str, Any]) -> AgentResult:
        papers = [Paper.from_dict(item) for item in task.get("papers", [])]
        if not papers and task.get("keyword"):
            papers = self.paper_service.search_papers(task["keyword"], years=task.get("years"), top_k=int(task.get("top_k", 4)))
        compare_items = self.paper_service.compare(papers)
        md = self.report_service.compare_to_markdown(compare_items)
        artifacts = self.report_service.export("paper_compare", md, [item.to_dict() for item in compare_items])
        return AgentResult("paper_compare", "ok", compare_items, f"Compared {len(compare_items)} papers.", artifacts)

    def _trend_analysis(self, task: dict[str, Any]) -> AgentResult:
        keyword = task.get("keyword", "")
        papers = self.paper_service.search_papers(keyword, years=task.get("years"), top_k=int(task.get("top_k", 20)))
        enriched = self.paper_service.summarize_and_enrich(papers, with_architecture=False)
        trend = self.review_service.analyze_trends(keyword, enriched)
        md = self.report_service.trend_to_markdown(trend)
        artifacts = self.report_service.export("trend_analysis", md, trend)
        return AgentResult("trend_analysis", "ok", trend, "Trend analysis generated.", artifacts)
