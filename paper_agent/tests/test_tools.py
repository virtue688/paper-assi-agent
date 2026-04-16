from pathlib import Path
from uuid import uuid4

from models.schemas import Paper
from tools.figure_tool import FigureTool
from tools.storage_tool import StorageTool


def _workspace_tmp() -> Path:
    path = Path("data/cache/test_runs") / uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_storage_dedup():
    storage = StorageTool(base_dir=str(_workspace_tmp()))
    paper = Paper(title="A Test Paper", paper_id="abc")
    assert storage.filter_new([paper]) == [paper]
    storage.mark_seen([paper])
    assert storage.filter_new([paper]) == []


def test_figure_fallback():
    tool = FigureTool(output_dir=str(_workspace_tmp()))
    paper = Paper(title="Vision Language Navigation", abstract="A transformer model with language and image inputs.")
    image_path, text = tool.extract_architecture(paper)
    assert image_path == ""
    assert "Architecture fallback" in text
