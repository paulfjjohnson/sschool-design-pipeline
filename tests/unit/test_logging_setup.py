from pathlib import Path

from app.utils.logging import configure_logging


def test_project_logger_writes_structured_file(tmp_path: Path) -> None:
    logger = configure_logging(tmp_path, "INFO")

    logger.info("startup")

    log_text = (tmp_path / "school_design_pipeline.log").read_text(encoding="utf-8")
    assert "startup" in log_text
    assert "INFO" in log_text
