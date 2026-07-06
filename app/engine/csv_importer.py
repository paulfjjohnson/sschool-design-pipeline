from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.data.models import SchoolRecord, SchoolStatus
from app.engine.colors import ColorLibrary, UnknownColorError
from app.engine.initials import InitialGenerator
from app.utils.errors import ErrorCategory, PipelineError
from app.utils.paths import sanitize_filename


class CsvSchemaError(PipelineError):
    def __init__(self, missing_columns: set[str]) -> None:
        columns = ", ".join(sorted(missing_columns))
        super().__init__(
            f"CSV is missing required columns: {columns}",
            category=ErrorCategory.DATA,
            suggested_resolution="Add the required columns and reload the CSV.",
        )


class CsvImporter:
    required_columns = {"School", "Mascot", "Color 1", "Color 2"}

    def __init__(self, color_library: ColorLibrary, initial_generator: InitialGenerator) -> None:
        self.color_library = color_library
        self.initial_generator = initial_generator

    def import_file(self, path: Path) -> list[SchoolRecord]:
        frame = pd.read_csv(path, dtype=str).fillna("")
        missing = self.required_columns - set(frame.columns)
        if missing:
            raise CsvSchemaError(missing)

        rows: list[SchoolRecord] = []
        seen_filenames: set[str] = set()
        for index, row in frame.iterrows():
            school_name = str(row["School"]).strip()
            mascot = str(row["Mascot"]).strip()
            primary = str(row["Color 1"]).strip()
            secondary = str(row["Color 2"]).strip()
            initial_result = self.initial_generator.generate(school_name)
            export_filename = sanitize_filename(f"{school_name}_FloralVarsity")
            notes: list[str] = []
            status = SchoolStatus.PENDING

            if initial_result.needs_review:
                status = SchoolStatus.NEEDS_REVIEW
                notes.append(initial_result.reason)
            if not mascot:
                status = SchoolStatus.NEEDS_REVIEW
                notes.append("Mascot is required for the data model.")
            for label, value in (("Color 1", primary), ("Color 2", secondary)):
                if not value:
                    status = SchoolStatus.NEEDS_REVIEW
                    notes.append(f"{label} is required.")
                    continue
                try:
                    self.color_library.resolve(value)
                except UnknownColorError as exc:
                    status = SchoolStatus.NEEDS_REVIEW
                    notes.append(str(exc))

            if export_filename in seen_filenames:
                status = SchoolStatus.NEEDS_REVIEW
                notes.append(f"Duplicate output filename: {export_filename}")
            seen_filenames.add(export_filename)

            rows.append(
                SchoolRecord(
                    row_number=int(index) + 1,
                    school_name=school_name,
                    mascot=mascot,
                    color_primary=primary,
                    color_secondary=secondary,
                    initials=initial_result.initials,
                    export_filename=export_filename,
                    status=status,
                    notes=" ".join(notes),
                )
            )
        return rows
