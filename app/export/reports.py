from __future__ import annotations

import csv
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Sequence

from app.data.models import Project, QAResult, SchoolRecord


@dataclass(frozen=True, slots=True)
class ReportPaths:
    csv: Path
    html: Path


class ReportWriter:
    def __init__(self, report_dir: Path) -> None:
        self.report_dir = report_dir

    def write_batch_summary(
        self,
        project: Project,
        records: Sequence[SchoolRecord],
        qa_results: Sequence[QAResult],
    ) -> ReportPaths:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        csv_path = self.report_dir / "batch_summary.csv"
        html_path = self.report_dir / "batch_summary.html"
        qa_by_school = {result.school: result for result in qa_results}

        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["row", "school", "status", "qa", "output", "notes"])
            for record in records:
                qa = qa_by_school.get(record.school_name)
                writer.writerow(
                    [
                        record.row_number,
                        record.school_name,
                        record.status.value,
                        "Passed" if qa and qa.passed else record.qa_status.value,
                        record.export_filename,
                        record.notes,
                    ]
                )

        rows = "\n".join(
            "<tr>"
            f"<td>{record.row_number}</td>"
            f"<td>{escape(record.school_name)}</td>"
            f"<td>{escape(record.status.value)}</td>"
            f"<td>{escape(record.qa_status.value)}</td>"
            f"<td>{escape(record.export_filename)}</td>"
            f"<td>{escape(record.notes)}</td>"
            "</tr>"
            for record in records
        )
        html_path.write_text(
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{escape(project.project_name)} Batch Summary</title>"
            "<style>body{font-family:Segoe UI,Arial,sans-serif}"
            "table{border-collapse:collapse;width:100%}"
            "th,td{border:1px solid #ccc;padding:6px;text-align:left}</style>"
            "</head><body>"
            f"<h1>{escape(project.project_name)} Batch Summary</h1>"
            "<table><thead><tr><th>Row</th><th>School</th><th>Status</th>"
            "<th>QA</th><th>Output</th><th>Notes</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></body></html>",
            encoding="utf-8",
        )
        return ReportPaths(csv=csv_path, html=html_path)
