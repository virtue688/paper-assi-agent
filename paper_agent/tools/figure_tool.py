from __future__ import annotations

from pathlib import Path

from models.schemas import Paper


class FigureTool:
    """Heuristic architecture extractor with explicit text fallback."""

    def __init__(self, output_dir: str = "data/papers/figures") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_architecture(self, paper: Paper, pdf_path: str = "", pdf_text: str = "") -> tuple[str, str]:
        image_path = self._try_extract_overview_figure(pdf_path, paper.dedup_key)
        if image_path:
            return image_path, "Detected a likely overview figure from the PDF using heuristic image extraction."
        return "", self._build_architecture_text(paper, pdf_text)

    def _try_extract_overview_figure(self, pdf_path: str, paper_key: str) -> str:
        if not pdf_path or not Path(pdf_path).exists():
            return ""
        try:
            import fitz  # type: ignore

            doc = fitz.open(pdf_path)
            for page_index in range(min(4, len(doc))):
                page = doc[page_index]
                page_text = page.get_text("text").lower()
                if not any(token in page_text for token in ["overview", "architecture", "framework", "pipeline", "model"]):
                    continue
                images = page.get_images(full=True)
                if not images:
                    continue
                extracted = doc.extract_image(images[0][0])
                safe_key = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in paper_key)[:80] or "paper"
                path = self.output_dir / f"{safe_key}_overview.{extracted.get('ext', 'png')}"
                path.write_bytes(extracted["image"])
                return str(path)
        except Exception:
            return ""
        return ""

    def _build_architecture_text(self, paper: Paper, pdf_text: str) -> str:
        evidence = f"{paper.title}. {paper.abstract} {pdf_text[:1200]}".lower()
        backbone = "Transformer / foundation model backbone" if "transformer" in evidence or "clip" in evidence else "task-specific neural backbone"
        modules = []
        if "language" in evidence or "text" in evidence:
            modules.append("language encoder")
        if "vision" in evidence or "image" in evidence:
            modules.append("visual encoder")
        if "diffusion" in evidence:
            modules.append("diffusion denoising module")
        if "segmentation" in evidence:
            modules.append("mask decoder")
        if "navigation" in evidence:
            modules.append("policy/planning module")
        if not modules:
            modules = ["feature encoder", "fusion module", "prediction head"]
        return (
            "Architecture fallback: no stable overview figure was extracted. "
            f"Input: task-specific text/image/state signals. Backbone: {backbone}. "
            f"Core modules: {', '.join(dict.fromkeys(modules))}. "
            "Output: predictions aligned with the paper task, such as labels, regions, actions, or masks."
        )
