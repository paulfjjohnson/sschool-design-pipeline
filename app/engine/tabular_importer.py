from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True, slots=True)
class TabularBatch:
    source_path: Path
    columns: list[str]
    rows: list[dict[str, str]]


class TabularImporter:
    def import_file(self, path: Path) -> TabularBatch:
        suffix = path.suffix.lower()
        if suffix not in {".csv", ".xlsx"}:
            raise ValueError("Batch file must be CSV or XLSX.")
        if suffix == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                header = next(csv.reader(handle), [])
            if len(header) != len(set(header)):
                raise ValueError("Duplicate spreadsheet column names are not allowed.")
            frame = pd.read_csv(path, dtype=str)
        else:
            frame = pd.read_excel(path, dtype=str, engine="openpyxl")
        columns = [str(column).strip() for column in frame.columns]
        if not all(columns) or len(columns) != len(set(columns)):
            raise ValueError("Spreadsheet columns must be unique and non-empty.")
        frame.columns = columns
        frame = frame.fillna("")
        rows = [
            {column: str(value).strip() for column, value in row.items()}
            for row in frame.to_dict(orient="records")
        ]
        return TabularBatch(path.resolve(), columns, rows)
