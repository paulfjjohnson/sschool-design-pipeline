from __future__ import annotations

from dataclasses import dataclass
from threading import Event
from typing import Sequence

from app.controller.progress import ProgressService
from app.data.models import QAResult, QAStatus, SchoolRecord, SchoolStatus, Template
from app.engine.image_engine import PngTemplateEngine
from app.export.exporter import PngExporter
from app.export.reports import ReportWriter
from app.qa.service import QAService


@dataclass(frozen=True, slots=True)
class BatchResult:
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    skipped_completed: int = 0


class BatchProcessor:
    def __init__(
        self,
        image_engine: PngTemplateEngine,
        qa_service: QAService,
        exporter: PngExporter,
    ) -> None:
        self.image_engine = image_engine
        self.qa_service = qa_service
        self.exporter = exporter
        self._paused = False
        self._stopped = False
        self._running = Event()
        self._running.set()

    @classmethod
    def default(cls) -> BatchProcessor:
        return cls(PngTemplateEngine(allow_default_font=True), QAService(), PngExporter())

    def pause(self) -> None:
        self._paused = True
        self._running.clear()

    def resume(self) -> None:
        self._paused = False
        self._running.set()

    def stop(self) -> None:
        self._stopped = True
        self._running.set()

    def start(self, project, template: Template, queue: Sequence[SchoolRecord]) -> BatchResult:
        self._stopped = False
        progress = ProgressService(project.progress_path)
        state = progress.load()
        completed_rows = set(state.completed_rows)
        completed = 0
        failed = 0
        skipped = 0
        skipped_completed = 0
        qa_results: list[QAResult] = []

        for record in queue:
            self._running.wait()
            if self._stopped:
                break
            if record.row_number in completed_rows:
                skipped_completed += 1
                continue
            if record.status is SchoolStatus.SKIPPED:
                progress.mark_skipped(record)
                skipped += 1
                continue
            if record.status is SchoolStatus.NEEDS_REVIEW:
                record.status = SchoolStatus.FAILED
                record.qa_status = QAStatus.FAILED
                progress.mark_failed(record)
                failed += 1
                continue

            record.status = SchoolStatus.PROCESSING
            try:
                render = self.image_engine.render(template, record)
                qa = self.qa_service.validate(render, record)
                qa_results.append(qa)
                if not qa.passed:
                    record.status = SchoolStatus.FAILED
                    record.qa_status = QAStatus.FAILED
                    record.notes = " ".join(qa.failures)
                    progress.mark_failed(record)
                    failed += 1
                    continue
                self.exporter.export(render, record, project.output_path, qa)
                record.status = SchoolStatus.COMPLETED
                record.qa_status = QAStatus.PASSED
                progress.mark_completed(record, qa)
                completed += 1
            except Exception as exc:  # noqa: BLE001 - convert row failures into resumable state.
                record.status = SchoolStatus.FAILED
                record.qa_status = QAStatus.FAILED
                record.notes = str(exc)
                progress.mark_failed(record)
                failed += 1

        ReportWriter(project.root_path / "reports").write_batch_summary(project, queue, qa_results)
        return BatchResult(
            completed=completed,
            failed=failed,
            skipped=skipped,
            skipped_completed=skipped_completed,
        )

    def reprocess_failed(
        self,
        project,
        template: Template,
        queue: Sequence[SchoolRecord],
    ) -> BatchResult:
        failed_rows = set(ProgressService(project.progress_path).load().failed_rows)
        target_rows = [record for record in queue if record.row_number in failed_rows]
        self._remove_failed_from_progress(project, target_rows)
        return self.start(project, template, target_rows)

    @staticmethod
    def _remove_failed_from_progress(project, rows: Sequence[SchoolRecord]) -> None:
        service = ProgressService(project.progress_path)
        progress = service.load()
        retry_numbers = {row.row_number for row in rows}
        progress.failed_rows = [row for row in progress.failed_rows if row not in retry_numbers]
        service.save(progress)

