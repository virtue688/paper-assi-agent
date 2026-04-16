from __future__ import annotations

from collections import OrderedDict
from typing import Iterable

from models.schemas import CompareItem, Paper
from tools import ArxivTool, FigureTool, OllamaLLM, PDFTool, SemanticScholarTool, StorageTool


class PaperService:
    def __init__(
        self,
        arxiv_tool: ArxivTool,
        semantic_tool: SemanticScholarTool,
        pdf_tool: PDFTool,
        figure_tool: FigureTool,
        llm: OllamaLLM,
        storage: StorageTool,
    ) -> None:
        self.arxiv_tool = arxiv_tool
        self.semantic_tool = semantic_tool
        self.pdf_tool = pdf_tool
        self.figure_tool = figure_tool
        self.llm = llm
        self.storage = storage

    def search_papers(self, keyword: str, years: int | None = None, top_k: int = 10) -> list[Paper]:
        arxiv = self.arxiv_tool.search(keyword, max_results=top_k, years=years)
        semantic = self.semantic_tool.search(keyword, max_results=top_k, years=years)
        return self.deduplicate([*arxiv, *semantic])[:top_k]

    def search_many_keywords(self, keywords: Iterable[str], years: int | None = None, top_k: int = 10) -> list[Paper]:
        papers: list[Paper] = []
        for keyword in keywords:
            papers.extend(self.search_papers(keyword, years=years, top_k=top_k))
        return self.deduplicate(papers)

    def deduplicate(self, papers: list[Paper]) -> list[Paper]:
        result: OrderedDict[str, Paper] = OrderedDict()
        for paper in papers:
            if paper.title:
                result.setdefault(paper.dedup_key, paper)
        return list(result.values())

    def summarize_and_enrich(self, papers: list[Paper], with_architecture: bool = True) -> list[Paper]:
        for paper in papers:
            text = f"Title: {paper.title}\nAbstract: {paper.abstract}"
            paper.summary = self.llm.summarize_text(text)
            paper.highlights = self._extract_highlights(paper)
            paper.method_tags = self._tag_methods(paper)
            if with_architecture:
                pdf_path = self.pdf_tool.download_pdf(paper.pdf_url, paper.dedup_key)
                pdf_text = self.pdf_tool.extract_text(pdf_path) if pdf_path else ""
                image_path, arch_text = self.figure_tool.extract_architecture(paper, pdf_path, pdf_text)
                paper.architecture_image_path = image_path
                paper.architecture_text = arch_text
        return papers

    def filter_new_and_mark(self, papers: list[Paper]) -> list[Paper]:
        new_papers = self.storage.filter_new(papers)
        self.storage.mark_seen(new_papers)
        return new_papers

    def compare(self, papers: list[Paper]) -> list[CompareItem]:
        enriched = self.summarize_and_enrich(papers, with_architecture=True)
        items: list[CompareItem] = []
        for paper in enriched:
            tags = ", ".join(paper.method_tags) or "general method"
            items.append(
                CompareItem(
                    title=paper.title,
                    task=self._infer_task(paper),
                    innovation="; ".join(paper.highlights[:2]) or "Not enough evidence in metadata.",
                    architecture=paper.architecture_text or "No architecture evidence available.",
                    experiments=f"Likely evaluated on task benchmarks related to {tags}.",
                    strengths="Clear relevance to the target research topic; metadata-level summary available.",
                    limitations="Full paper parsing is needed for precise ablations and quantitative claims.",
                    best_for=f"Researchers tracking {tags}.",
                )
            )
        return items

    def _extract_highlights(self, paper: Paper) -> list[str]:
        text = f"{paper.title}. {paper.abstract}".lower()
        highlights = []
        if "open" in text or "zero-shot" in text:
            highlights.append("Emphasizes open-set or zero-shot generalization.")
        if "language" in text or "text" in text:
            highlights.append("Uses language signals to guide perception or reasoning.")
        if "diffusion" in text:
            highlights.append("Uses diffusion-style generation or policy modeling.")
        if "benchmark" in text or "dataset" in text:
            highlights.append("Includes benchmark or dataset-driven evaluation.")
        return highlights or ["Addresses the target task with a model-centric method."]

    def _tag_methods(self, paper: Paper) -> list[str]:
        text = f"{paper.title}. {paper.abstract}".lower()
        mapping = {
            "vision-language": ["vision-language", "multimodal", "clip", "text"],
            "detection": ["detection", "detector", "object"],
            "segmentation": ["segmentation", "mask"],
            "navigation": ["navigation", "embodied", "policy"],
            "diffusion": ["diffusion", "denoising"],
            "transformer": ["transformer", "attention"],
            "retrieval": ["retrieval", "ranking"],
        }
        tags = [name for name, keys in mapping.items() if any(key in text for key in keys)]
        return tags or ["general"]

    def _infer_task(self, paper: Paper) -> str:
        tags = self._tag_methods(paper)
        if "detection" in tags:
            return "Object detection / grounding"
        if "segmentation" in tags:
            return "Segmentation"
        if "navigation" in tags:
            return "Embodied navigation"
        if "diffusion" in tags:
            return "Generative policy/modeling"
        return "Research task inferred from title and abstract"
