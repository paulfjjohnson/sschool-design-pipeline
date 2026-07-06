# Requirements Traceability

| Requirement | Implementation |
| --- | --- |
| Native Windows desktop app | `app/main.py`, `app/ui/main_window.py`, PySide6 |
| Deterministic template editing | `app/engine/image_engine.py` |
| Never recreate artwork | PNG engine edits copies of master templates only |
| Registered editable regions only | `TemplateRegistry`, masks, `LockedRegionComparator` |
| CSV required columns | `CsvImporter.required_columns` |
| Natural initials | `InitialGenerator` |
| Color mapping | `ColorLibrary` |
| QA before export | `BatchProcessor`, `QAService`, `PngExporter` |
| Transparent PNG 300 DPI | `PngExporter` |
| Progress recovery | `ProgressService` |
| Logs | `configure_logging` |
| Reports | `ReportWriter` |
| Plugin architecture | `app/plugins/api.py`, `app/plugins/manager.py` |
| Unit tests | `tests/unit/` |
| Integration tests | `tests/integration/` |
| Golden master tests | `tests/golden/` |
| Resume tests | `tests/integration/test_resume_project.py` |
| System acceptance | `tests/system/test_sample_project_acceptance.py` |

