from pathlib import Path

import pytest

from app.data.models import SchoolStatus
from app.engine.colors import ColorLibrary
from app.engine.csv_importer import CsvImporter, CsvSchemaError
from app.engine.initials import InitialGenerator


def test_csv_importer_builds_pending_queue(tmp_path: Path) -> None:
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text(
        "School,Mascot,Color 1,Color 2\n"
        "Pecan Grove Primary,Pelicans,Red,Royal\n"
        "Gonzales Primary,Bulldogs,Green,Yellow\n",
        encoding="utf-8",
    )

    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(csv_path)

    assert [row.initials for row in rows] == ["PGP", "GP"]
    assert rows[0].status is SchoolStatus.PENDING
    assert rows[0].export_filename == "Pecan_Grove_Primary_FloralVarsity.png"


def test_unknown_color_marks_row_needs_review(tmp_path: Path) -> None:
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text(
        "School,Mascot,Color 1,Color 2\n"
        "Sugar Mill Primary,Eagles,Maroon,Royal\n",
        encoding="utf-8",
    )

    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(csv_path)

    assert rows[0].status is SchoolStatus.NEEDS_REVIEW
    assert "not mapped" in rows[0].notes


def test_duplicate_filenames_are_flagged(tmp_path: Path) -> None:
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text(
        "School,Mascot,Color 1,Color 2\n"
        "Carver Primary,Bears,Red,Royal\n"
        "Carver Primary,Cats,Red,Royal\n",
        encoding="utf-8",
    )

    rows = CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(csv_path)

    assert rows[0].status is SchoolStatus.PENDING
    assert rows[1].status is SchoolStatus.NEEDS_REVIEW
    assert "Duplicate output filename" in rows[1].notes


def test_missing_required_columns_raise_schema_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text("School,Mascot,Color 1\nCarver Primary,Bears,Red\n", encoding="utf-8")

    with pytest.raises(CsvSchemaError, match="Color 2"):
        CsvImporter(ColorLibrary.default(), InitialGenerator()).import_file(csv_path)
