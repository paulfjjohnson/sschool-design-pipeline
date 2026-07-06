from __future__ import annotations

from pathlib import Path

from app.data.models import QAResult, QAStatus, SchoolRecord
from app.engine.image_engine import RenderResult
from app.utils.errors import QABlockedExportError


class PngExporter:
    def __init__(self, dpi: int = 300) -> None:
        self.dpi = dpi

    def export(
        self,
        render: RenderResult,
        record: SchoolRecord,
        output_dir: Path,
        qa: QAResult,
    ) -> Path:
        if not qa.passed:
            raise QABlockedExportError("QA failed; export is blocked.")
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / record.export_filename
        render.image.save(path, "PNG", dpi=(self.dpi, self.dpi), compress_level=6)
        qa.export_check = QAStatus.PASSED
        return path
