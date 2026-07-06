from pathlib import Path

import pandas as pd

from app.engine.tabular_importer import TabularImporter


def test_csv_and_xlsx_normalize_identically(tmp_path: Path) -> None:
    frame = pd.DataFrame([{"Name": "Alpha", "Logo File": "assets/a.png", "Visible": "yes"}])
    csv_path, xlsx_path = tmp_path / "rows.csv", tmp_path / "rows.xlsx"
    frame.to_csv(csv_path, index=False)
    frame.to_excel(xlsx_path, index=False)
    assert TabularImporter().import_file(csv_path).rows == TabularImporter().import_file(xlsx_path).rows


def test_importer_rejects_duplicate_columns(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("Name,Name\nA,B\n", encoding="utf-8")
    try:
        TabularImporter().import_file(path)
    except ValueError as exc:
        assert "Duplicate" in str(exc)
    else:
        raise AssertionError("Expected duplicate columns to fail")
