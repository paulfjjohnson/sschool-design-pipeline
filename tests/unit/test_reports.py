from pathlib import Path

from app.data.models import Project, QAResult, SchoolRecord
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

