from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar
from uuid import uuid4


SCHEMA_VERSION = "1.0"


class SchoolStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    SKIPPED = "Skipped"
    NEEDS_REVIEW = "NeedsReview"


class QAStatus(str, Enum):
    NOT_RUN = "NotRun"
    PASSED = "Passed"
    FAILED = "Failed"
    WARNING = "Warning"


class RegionType(str, Enum):
    TEXT = "TEXT"
    COLOR = "COLOR"
    MASK = "MASK"
    GROUP = "GROUP"
    VECTOR = "VECTOR"


@dataclass(slots=True)
class AppSettings:
    schema_version: str = SCHEMA_VERSION
    default_project_folder: Path = Path("projects")
    default_output_folder: Path = Path("output")
    autosave_interval_seconds: int = 60
    backup_interval_seconds: int = 300
    default_dpi: int = 300
    default_export_width: int = 3600
    default_export_height: int = 3600
    export_format: str = "PNG"
    transparent_background: bool = True
    compression_level: int = 6
    log_level: str = "INFO"
    theme: str = "system"
    language: str = "en"
    maximum_worker_threads: int = 1
    stop_on_failure: bool = False
    run_qa_before_export: bool = True
    save_preview_thumbnails: bool = False


@dataclass(slots=True)
class ProjectSettings:
    color_library_path: Path | None = None
    font_library_path: Path | None = None
    qa_profile: str = "standard"
    export_profile: str = "png_300dpi"
    stop_on_failure: bool = False
    run_qa_before_export: bool = True


@dataclass(slots=True)
class EditableRegion:
    region_id: str
    name: str
    region_type: RegionType
    x: int
    y: int
    width: int
    height: int
    rotation: float = 0.0
    locked: bool = False
    mask_path: Path | None = None
    selector: str | None = None


@dataclass(slots=True)
class Template:
    template_id: str
    name: str
    version: str
    format: str
    source_path: Path
    editable_regions: list[EditableRegion]
    geometry_checksum: str
    output_width: int
    output_height: int
    default_font: Path | None = None
    script_font: Path | None = None
    engine_version: str = "1.0"


@dataclass(slots=True)
class ColorDefinition:
    display_name: str
    hex: str
    rgb: tuple[int, int, int]
    aliases: list[str] = field(default_factory=list)
    cmyk: tuple[int, int, int, int] | None = None


@dataclass(slots=True)
class SchoolRecord:
    row_number: int
    school_name: str
    mascot: str
    color_primary: str
    color_secondary: str
    initials: str
    export_filename: str
    status: SchoolStatus = SchoolStatus.PENDING
    qa_status: QAStatus = QAStatus.NOT_RUN
    notes: str = ""

    @classmethod
    def example(cls, row_number: int = 1) -> SchoolRecord:
        return cls(
            row_number=row_number,
            school_name=f"Example Primary {row_number}",
            mascot="Eagles",
            color_primary="Red",
            color_secondary="Royal",
            initials=f"EP{row_number}",
            export_filename=f"Example_Primary_{row_number}_FloralVarsity.png",
        )


@dataclass(slots=True)
class Progress:
    schema_version: str = SCHEMA_VERSION
    current_index: int = 0
    completed_rows: list[int] = field(default_factory=list)
    failed_rows: list[int] = field(default_factory=list)
    skipped_rows: list[int] = field(default_factory=list)
    last_processed: str | None = None
    elapsed_time_seconds: float = 0.0


@dataclass(slots=True)
class QAResult:
    school: str
    passed: bool
    warnings: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    geometry_check: QAStatus = QAStatus.NOT_RUN
    transparency_check: QAStatus = QAStatus.NOT_RUN
    spelling_check: QAStatus = QAStatus.NOT_RUN
    export_check: QAStatus = QAStatus.NOT_RUN

    @classmethod
    def passed_for(cls, record: SchoolRecord) -> QAResult:
        return cls(
            school=record.school_name,
            passed=True,
            geometry_check=QAStatus.PASSED,
            transparency_check=QAStatus.PASSED,
            spelling_check=QAStatus.PASSED,
            export_check=QAStatus.PASSED,
        )

    @classmethod
    def failed_for(cls, record: SchoolRecord, rule: str, reason: str) -> QAResult:
        return cls(school=record.school_name, passed=False, failures=[f"{rule}: {reason}"])


@dataclass(slots=True)
class Project:
    project_id: str
    project_name: str
    root_path: Path
    template_id: str | None = None
    template_version: str | None = None
    csv_path: Path | None = None
    output_path: Path | None = None
    progress_path: Path | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def new(cls, project_name: str, root_path: Path) -> Project:
        return cls(
            project_id=str(uuid4()),
            project_name=project_name,
            root_path=root_path,
            output_path=root_path / "output",
            progress_path=root_path / "progress.json",
        )

    @classmethod
    def example(cls, root_path: Path) -> Project:
        return cls.new("Example Project", root_path)


T = TypeVar("T")


def to_primitive(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple):
        return [to_primitive(item) for item in value]
    if isinstance(value, list):
        return [to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in value.items()}
    return value

