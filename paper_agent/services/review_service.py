from __future__ import annotations

from collections import defaultdict

from models.schemas import Paper, ReviewReport
from tools import OllamaLLM


class ReviewService:
    def __init__(self, llm: OllamaLLM) -> None:
        self.llm = llm

    def classify_routes(self, papers: list[Paper]) -> dict[str, list[str]]:
        routes: dict[str, list[str]] = defaultdict(list)
        for paper in papers:
            for tag in (paper.method_tags or ["general"])[:2]:
                routes[tag].append(paper.title)
        return dict(routes)

    def build_review(self, keyword: str, papers: list[Paper]) -> ReviewReport:
        routes = self.classify_routes(papers)
        evidence = "\n".join(f"- {paper.title}: {paper.summary or paper.abstract[:300]}" for paper in papers)
        prompt = (
            f"Write an academic-style Chinese literature review for topic: {keyword}.\n"
            "Synthesize the field instead of concatenating abstracts.\n"
            f"{evidence}\n"
            "Cover background, problem definition, taxonomy, datasets/metrics, challenges, and future work."
        )
        generated = self.llm.generate(prompt)
        background = generated[:1200] if generated and not generated.startswith("[LLM fallback]") else (
            f"{keyword} focuses on building robust research systems under realistic data and evaluation constraints."
        )
        return ReviewReport(
            title=f"{keyword} Research Review",
            background=background,
            problem_definition=f"The core problem is to model, reason, and evaluate {keyword} with reliable generalization.",
            technical_routes=routes,
            representative_methods=[f"{paper.title}: {paper.summary[:240]}" for paper in papers[:8]],
            datasets_and_metrics=self._infer_datasets_metrics(papers),
            challenges=[
                "Generalization across domains and long-tail concepts remains difficult.",
                "Evaluation protocols may not fully reflect real deployment conditions.",
                "Architecture and training details are often hard to compare across papers.",
            ],
            future_directions=[
                "Stronger foundation-model adaptation with controllable evaluation.",
                "Better data curation, benchmark design, and failure analysis.",
                "More transparent system-level comparisons and reproducible pipelines.",
            ],
            references=[paper.to_dict() for paper in papers],
        )

    def analyze_trends(self, keyword: str, papers: list[Paper]) -> dict:
        by_year: dict[int, list[str]] = defaultdict(list)
        backbone_counter: dict[str, int] = defaultdict(int)
        route_counter: dict[str, int] = defaultdict(int)
        datasets: set[str] = set()
        metrics: set[str] = set()
        for paper in papers:
            if paper.year:
                by_year[paper.year].append(paper.title)
            text = f"{paper.title} {paper.abstract}".lower()
            for backbone in ["transformer", "clip", "vit", "diffusion", "llm", "cnn"]:
                if backbone in text:
                    backbone_counter[backbone] += 1
            for tag in paper.method_tags or ["general"]:
                route_counter[tag] += 1
            for dataset in ["coco", "imagenet", "scannet", "matterport", "habitat", "ade20k", "refcoco"]:
                if dataset in text:
                    datasets.add(dataset)
            for metric in ["accuracy", "map", "miou", "success rate", "spl", "f1"]:
                if metric in text:
                    metrics.add(metric)
        return {
            "keyword": keyword,
            "timeline": [{"year": year, "papers": titles} for year, titles in sorted(by_year.items())],
            "main_routes": sorted(route_counter, key=route_counter.get, reverse=True),
            "common_backbones_or_modules": sorted(backbone_counter, key=backbone_counter.get, reverse=True),
            "hot_datasets": sorted(datasets) or ["dataset evidence not explicit in metadata"],
            "hot_metrics": sorted(metrics) or ["metric evidence not explicit in metadata"],
            "evolution": (
                "Recent work tends to move from task-specific architectures toward foundation-model, "
                "multimodal, and data-centric pipelines with stronger generalization claims."
            ),
        }

    def _infer_datasets_metrics(self, papers: list[Paper]) -> list[str]:
        joined = " ".join(f"{paper.title} {paper.abstract}" for paper in papers).lower()
        found = []
        for item in ["COCO", "ImageNet", "RefCOCO", "ADE20K", "ScanNet", "Matterport3D", "Habitat", "mAP", "mIoU", "SPL"]:
            if item.lower() in joined:
                found.append(item)
        return found or ["Metadata does not expose datasets/metrics clearly; parse PDFs for stronger evidence."]
