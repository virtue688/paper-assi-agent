from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests


class PDFTool:
    def __init__(self, paper_dir: str = "data/papers", timeout: int = 30) -> None:
        self.paper_dir = Path(paper_dir)
        self.paper_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout

    def download_pdf(self, pdf_url: str, paper_key: str) -> str:
        if not pdf_url:
            return ""
        safe_key = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in paper_key)[:80] or "paper"
        path = self.paper_dir / f"{safe_key}.pdf"
        if path.exists():
            return str(path)
        try:
            response = requests.get(pdf_url, timeout=self.timeout)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" not in content_type and not urlparse(pdf_url).path.endswith(".pdf"):
                return ""
            path.write_bytes(response.content)
            return str(path)
        except requests.RequestException:
            return ""

    def extract_text(self, pdf_path: str, max_pages: int = 3) -> str:
        if not pdf_path or not Path(pdf_path).exists():
            return ""
        try:
            import fitz  # type: ignore

            doc = fitz.open(pdf_path)
            return "\n".join(doc[index].get_text("text") for index in range(min(max_pages, len(doc))))
        except Exception:
            return ""
