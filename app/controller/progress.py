from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Sequence

from app.data.models import Progress, QAResult, SchoolRecord
from app.data.serialization import read_json
from app.utils.errors import ErrorCategory, PipelineError


class ProgressStateError(PipelineError):
    def __init__(self, message: str) -> None:
        super().__init__(message, category=ErrorCategory.PROJECT)


class ProgressService:
    def __init__(self, progress_path: Path) -> None:
        self.progress_path = progress_path

    def load(self) -> Progress:
        if not self.progress_path.exists():
            return Progress()
        try:
            return read_json(self.progress_path, Progress)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ProgressStateError(f"Invalid progress file: {self.progress_path}") from exc

    def save(self, progress: Progress) -> None:
        self.progress_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": progress.schema_version,
            "current_index": progress.current_index,
            "completed_rows": progress.completed_rows,
            "failed_rows": progress.failed_rows,
            "skipped_rows": progress.skipped_rows,
            "last_processed": progress.last_processed,
            "elapsed_time_seconds": progress.elapsed_time_seconds,
        }
        with NamedTemporaryFile(
            "w",
            delete=False,
            dir=self.progress_path.parent,
            encoding="utf-8",
            suffix=".tmp",
        ) as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            temp_name = handle.name
        os.replace(temp_name, self.progress_path)

    def mark_completed(self, row: SchoolRecord, qa: QAResult) -> None:
        progress = self.load()
        if row.row_number not in progress.completed_rows:
            progress.completed_rows.append(row.row_number)
        progress.current_index = max(progress.current_index, row.row_number)
        progress.last_processed = datetime.now(UTC).isoformat()
        self.save(progress)

    def mark_failed(self, row: SchoolRecord) -> None:
        progress = self.load()
        if row.row_number not in progress.failed_rows:
            progress.failed_rows.append(row.row_number)
        progress.current_index = max(progress.current_index, row.row_number)
        progress.last_processed = datetime.now(UTC).isoformat()
        self.save(progress)

    def mark_skipped(self, row: SchoolRecord) -> None:
        progress = self.load()
        if row.row_number not in progress.skipped_rows:
            progress.skipped_rows.append(row.row_number)
        progress.current_index = max(progress.current_index, row.row_number)
        progress.last_processed = datetime.now(UTC).isoformat()
        self.save(progress)

    def first_incomplete(self, records: Sequence[SchoolRecord]) -> int:
        progress = self.load()
        done = set(progress.completed_rows) | set(progress.failed_rows) | set(progress.skipped_rows)
        for index, record in enumerate(records):
            if record.row_number not in done:
                return index
        return len(records)

