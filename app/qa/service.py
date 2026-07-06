from __future__ import annotations

from app.data.models import QAResult, QAStatus, SchoolRecord
from app.engine.image_engine import LockedRegionComparator, RenderResult


class QAService:
    def validate(self, render: RenderResult, record: SchoolRecord) -> QAResult:
        failures: list[str] = []
        if render.record.initials != record.initials:
            failures.append("Initials do not match expected value.")
        if render.record.school_name != record.school_name:
            failures.append("School name does not match CSV value.")
        if LockedRegionComparator(render.template).unexpected_changed_pixels(render.image) != 0:
            failures.append("Locked pixels changed outside registered editable regions.")
        if render.image.mode != "RGBA":
            failures.append("Rendered image is not RGBA.")
        alpha_min, _alpha_max = render.image.getchannel("A").getextrema()
        if alpha_min == 255:
            failures.append("Transparency was not preserved.")

        passed = not failures
        status = QAStatus.PASSED if passed else QAStatus.FAILED
        return QAResult(
            school=record.school_name,
            passed=passed,
            failures=failures,
            geometry_check=status,
            transparency_check=status,
            spelling_check=status,
            export_check=QAStatus.NOT_RUN,
        )
