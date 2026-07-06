from __future__ import annotations

from enum import Enum


class ErrorSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class ErrorCategory(str, Enum):
    CONFIGURATION = "Configuration"
    PROJECT = "Project"
    TEMPLATE = "Template"
    DATA = "Data"
    TYPOGRAPHY = "Typography"
    PROCESSING = "Processing"
    QA = "QA"
    EXPORT = "Export"
    SYSTEM = "System"


class PipelineError(Exception):
    def __init__(
        self,
        message: str,
        *,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        suggested_resolution: str = "",
    ) -> None:
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.suggested_resolution = suggested_resolution


class ValidationError(PipelineError):
    pass


class QABlockedExportError(PipelineError):
    def __init__(self, message: str) -> None:
        super().__init__(message, category=ErrorCategory.EXPORT, severity=ErrorSeverity.ERROR)

