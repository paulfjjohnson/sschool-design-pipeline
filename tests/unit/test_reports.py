from pathlib import Path

from app.data.models import Project, QAResult, SchoolRecord, SchoolStatus
from app.export.reports import ReportWriter


def test_batch_summary_writes_csv_and_html(tmp_path: Path) -> None:
    record = SchoolRecord.example(row_number=1)
    paths = ReportWriter(tmp_path).write_batch_summary(
        Project.example(tmp_path),
        [record],
        [QAResult.passed_for(record)],
    )

    assert paths.csv.exists()
    assert paths.html.exists()
    assert "Example Primary 1" in paths.html.read_text(encoding="utf-8")


def test_batch_summary_writes_failed_items_report_with_reasons(tmp_path: Path) -> None:
    record = SchoolRecord.example(row_number=3)
    record.status = SchoolStatus.FAILED
    record.notes = "Mascot Pattern Text: pattern text requires a pattern_path."

    paths = ReportWriter(tmp_path).write_batch_summary(Project.example(tmp_path), [record], [])

    assert paths.failed_csv.exists()
    failure_report = paths.failed_csv.read_text(encoding="utf-8")
    assert "Example Primary 3" in failure_report
    assert "pattern text requires a pattern_path" in failure_report

