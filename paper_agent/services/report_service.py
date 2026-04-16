from __future__ import annotations

from datetime import datetime
from typing import Any

from models.schemas import CompareItem, Paper, ReviewReport
from tools import StorageTool


class ReportService:
    def __init__(self, storage: StorageTool) -> None:
        self.storage = storage

    def papers_to_markdown(self, title: str, keyword: str, papers: list[Paper]) -> str:
        lines = [
            f"# {title}",
            "",
            f"- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"- Keyword: {keyword}",
            f"- New/Returned papers: {len(papers)}",
            "",
        ]
        for index, paper in enumerate(papers, 1):
            lines.extend(
                [
                    f"## {index}. {paper.title}",
                    "",
                    f"- Link: {paper.url or paper.pdf_url}",
                    f"- Source: {paper.source}",
                    f"- Year: {paper.year or 'unknown'}",
                    f"- Authors: {', '.join(paper.authors[:6]) or 'unknown'}",
                    f"- Summary: {paper.summary}",
                    f"- Highlights: {'; '.join(paper.highlights)}",
                    f"- Method tags: {', '.join(paper.method_tags)}",
                    f"- Architecture image: {paper.architecture_image_path or 'not extracted'}",
                    f"- Architecture text: {paper.architecture_text}",
                    "",
                ]
            )
        return "\n".join(lines)

    def review_to_markdown(self, report: ReviewReport) -> str:
        lines = [
            f"# {report.title}",
            "",
            f"- Created at: {report.created_at}",
            "",
            "## Research Background",
            report.background,
            "",
            "## Problem Definition",
            report.problem_definition,
            "",
            "## Technical Routes",
        ]
        for route, titles in report.technical_routes.items():
            lines.append(f"- {route}: {len(titles)} papers")
        lines.extend(["", "## Representative Methods"])
        lines.extend(f"- {item}" for item in report.representative_methods)
        lines.extend(["", "## Datasets and Metrics"])
        lines.extend(f"- {item}" for item in report.datasets_and_metrics)
        lines.extend(["", "## Challenges"])
        lines.extend(f"- {item}" for item in report.challenges)
        lines.extend(["", "## Future Directions"])
        lines.extend(f"- {item}" for item in report.future_directions)
        lines.extend(["", "## References"])
        lines.extend(f"- {item.get('title')} ({item.get('year')}) {item.get('url')}" for item in report.references)
        return "\n".join(lines)

    def compare_to_markdown(self, items: list[CompareItem]) -> str:
        headers = ["Title", "Task", "Innovation", "Architecture", "Experiments", "Strengths", "Limitations", "Best For"]
        rows = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
        for item in items:
            values = [
                item.title,
                item.task,
                item.innovation,
                item.architecture,
                item.experiments,
                item.strengths,
                item.limitations,
                item.best_for,
            ]
            rows.append("| " + " | ".join(self._cell(value) for value in values) + " |")
        return "\n".join(["# Paper Comparison", "", *rows])

    def trend_to_markdown(self, trend: dict[str, Any]) -> str:
        lines = [f"# Trend Analysis: {trend.get('keyword', '')}", "", "## Timeline"]
        for item in trend.get("timeline", []):
            lines.append(f"- {item['year']}: {', '.join(item['papers'][:5])}")
        lines.append("\n## Main Routes")
        lines.extend(f"- {item}" for item in trend.get("main_routes", []))
        lines.append("\n## Common Backbones or Modules")
        lines.extend(f"- {item}" for item in trend.get("common_backbones_or_modules", []))
        lines.append("\n## Hot Datasets")
        lines.extend(f"- {item}" for item in trend.get("hot_datasets", []))
        lines.append("\n## Hot Metrics")
        lines.extend(f"- {item}" for item in trend.get("hot_metrics", []))
        lines.append("\n## Evolution")
        lines.append(trend.get("evolution", ""))
        return "\n".join(lines)

    def export(self, name: str, markdown: str, payload: Any) -> dict[str, str]:
        md_path = self.storage.save_report(name, markdown, suffix="md")
        json_payload = payload.to_dict() if hasattr(payload, "to_dict") else payload
        json_path = self.storage.save_result_json(name, json_payload)
        return {"markdown": md_path, "json": json_path}

    def _cell(self, value: str) -> str:
        return " ".join(str(value).replace("|", "/").split())
