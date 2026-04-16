from __future__ import annotations

from datetime import datetime
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

import requests

from models.schemas import Paper


class ArxivTool:
    API_URL = "http://export.arxiv.org/api/query"

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def search(self, keyword: str, max_results: int = 10, years: int | None = None) -> list[Paper]:
        query = quote_plus(f'all:"{keyword}"')
        url = f"{self.API_URL}?search_query={query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            papers = self._parse(response.text)
        except (requests.RequestException, ET.ParseError):
            papers = self._mock_results(keyword, max_results)
        if years:
            min_year = datetime.now().year - years + 1
            papers = [paper for paper in papers if not paper.year or paper.year >= min_year]
        return papers[:max_results]

    def _parse(self, xml_text: str) -> list[Paper]:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(xml_text)
        papers: list[Paper] = []
        for entry in root.findall("atom:entry", ns):
            title = " ".join(entry.findtext("atom:title", default="", namespaces=ns).split())
            abstract = " ".join(entry.findtext("atom:summary", default="", namespaces=ns).split())
            paper_id = entry.findtext("atom:id", default="", namespaces=ns)
            published_at = entry.findtext("atom:published", default="", namespaces=ns)
            year = int(published_at[:4]) if published_at[:4].isdigit() else None
            authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href", "")
            papers.append(
                Paper(
                    title=title,
                    abstract=abstract,
                    url=paper_id,
                    authors=[item for item in authors if item],
                    year=year,
                    venue="arXiv",
                    source="arxiv",
                    paper_id=paper_id,
                    pdf_url=pdf_url,
                    published_at=published_at,
                )
            )
        return papers

    def _mock_results(self, keyword: str, max_results: int) -> list[Paper]:
        return [
            Paper(
                title=f"Mock Paper on {keyword.title()}",
                abstract=(
                    f"This fallback paper discusses {keyword}, including task definition, model components, "
                    "training data, evaluation metrics, and open research challenges."
                ),
                url="https://arxiv.org/",
                authors=["Paper Agent Demo"],
                year=datetime.now().year,
                venue="arXiv fallback",
                source="mock_arxiv",
                paper_id=f"mock-arxiv-{keyword.lower().replace(' ', '-')}",
            )
        ][:max_results]
