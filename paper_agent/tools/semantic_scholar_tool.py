from __future__ import annotations

from datetime import datetime

import requests

from models.schemas import Paper


class SemanticScholarTool:
    API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self, api_key: str = "", timeout: int = 20) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def search(self, keyword: str, max_results: int = 10, years: int | None = None) -> list[Paper]:
        fields = "paperId,title,abstract,authors,year,venue,url,openAccessPdf,publicationDate"
        params = {"query": keyword, "limit": max_results, "fields": fields}
        if years:
            min_year = datetime.now().year - years + 1
            params["year"] = f"{min_year}-"
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        try:
            response = requests.get(self.API_URL, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return [self._to_paper(item) for item in response.json().get("data", []) if item.get("title")]
        except (requests.RequestException, ValueError):
            return []

    def _to_paper(self, item: dict) -> Paper:
        pdf = item.get("openAccessPdf") or {}
        return Paper(
            title=item.get("title", ""),
            abstract=item.get("abstract") or "",
            url=item.get("url") or "",
            authors=[author.get("name", "") for author in item.get("authors", []) if author.get("name")],
            year=item.get("year"),
            venue=item.get("venue") or "",
            source="semantic_scholar",
            paper_id=item.get("paperId") or "",
            pdf_url=pdf.get("url") or "",
            published_at=item.get("publicationDate") or "",
        )
