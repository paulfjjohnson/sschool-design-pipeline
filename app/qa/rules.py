from __future__ import annotations

from dataclasses import dataclass

from app.data.models import QAStatus


@dataclass(frozen=True, slots=True)
class RuleOutcome:
    name: str
    status: QAStatus
    message: str = ""

