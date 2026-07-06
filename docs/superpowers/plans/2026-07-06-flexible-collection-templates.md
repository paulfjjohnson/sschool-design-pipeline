# Flexible Collection Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace fixed Floral Varsity regions with ordered, schema-driven operations mapped to CSV/XLSX columns, defaults, and row assets.

**Architecture:** Versioned template operations are resolved against normalized row dictionaries and executed by isolated handlers. Legacy templates migrate in memory to equivalent operations; all operation masks are combined for locked-pixel QA.

**Tech Stack:** Python 3.12+, PySide6, Pillow, OpenCV, NumPy, pandas, openpyxl, PyYAML, pytest, PyInstaller.

## Global Constraints

- Windows 10/11 desktop only.
- Master templates and unregistered pixels remain immutable.
- Missing fonts, colors, columns, and assets never receive silent substitutions.
- CSV and XLSX imports must normalize identically.
- Existing schema version 1 projects remain loadable.

---

### Task 1: Version 2 Operation Models And Migration

**Files:** Modify `app/data/models.py`, `app/engine/templates.py`; create `app/engine/migration.py`; test `tests/unit/test_template_v2.py`.

**Interfaces:** Produce `OperationType`, `TemplateOperation`, `Template.schema_version`, and `migrate_template_v1(data, root)`.

- [ ] Write tests proving arbitrary ordered operations deserialize and legacy four-region metadata migrates.
- [ ] Run `python -m pytest tests/unit/test_template_v2.py -q` and verify failure.
- [ ] Implement enums, dataclasses, parser, validation, and migration.
- [ ] Run the focused tests and full legacy template tests.
- [ ] Commit `feat: add versioned template operations`.

### Task 2: CSV/XLSX Normalization And Asset Resolution

**Files:** Create `app/engine/tabular_importer.py`, `app/engine/assets.py`; modify `requirements.txt`; test `tests/unit/test_tabular_importer.py` and `tests/unit/test_assets.py`.

**Interfaces:** Produce `TabularImporter.import_file(path) -> TabularBatch` and `AssetResolver.resolve(value, spreadsheet_path) -> Path`.

- [ ] Write parity, relative-path, missing-file, and duplicate-column tests.
- [ ] Verify RED with focused pytest command.
- [ ] Implement pandas-backed CSV/XLSX normalization and strict asset resolution.
- [ ] Verify focused and importer regression tests.
- [ ] Commit `feat: add flexible CSV and Excel imports`.

### Task 3: Operation Resolution And Rendering

**Files:** Create `app/engine/operations.py`, `app/engine/operation_resolver.py`; modify `app/engine/image_engine.py`; test `tests/unit/test_operations.py` and `tests/golden/test_operation_locked_regions.py`.

**Interfaces:** Produce `OperationResolver.resolve(operation, row, source_path)` and handlers for `TEXT`, `SOLID_COLOR`, `PATTERN_FILL`, `IMAGE_REPLACE`, `VISIBILITY`, `LOCKED`.

- [ ] Write tests for defaults, overrides, layer order, text case, pattern treatment, image fit, visibility, and locked pixels.
- [ ] Verify RED.
- [ ] Implement handlers with strict effective masks and typed values.
- [ ] Verify focused, golden, and existing renderer tests.
- [ ] Commit `feat: add schema-driven operation renderer`.

### Task 4: Flexible Registration And Mapping UI

**Files:** Create `app/ui/operation_editor.py`; modify `app/ui/registration.py`, `app/ui/main_window.py`; test `tests/ui/test_operation_editor.py`.

**Interfaces:** Produce operation add/remove/reorder/type/mapping/default/override controls and sample-row preview.

- [ ] Write UI tests for adding, deleting, reordering, mapping, and validation.
- [ ] Verify RED.
- [ ] Implement operation list, properties editor, spreadsheet-column loader, and metadata save.
- [ ] Verify UI tests and manually capture a fitted large-image registration screenshot.
- [ ] Commit `feat: add flexible operation registration UI`.

### Task 5: Project Integration And Legacy Acceptance

**Files:** Modify `app/controller/app_controller.py`, `app/controller/batch.py`, `app/qa/service.py`; test `tests/integration/test_flexible_collection.py` and `tests/system/test_legacy_migration.py`.

**Interfaces:** Connect normalized rows, operation renderer, progress, QA, reports, Start, and Rebuild All.

- [ ] Write mixed text/color/pattern/image/visibility acceptance tests and legacy migration acceptance.
- [ ] Verify RED.
- [ ] Implement controller and batch integration with actionable row errors.
- [ ] Verify integration, system, resume, and report tests.
- [ ] Commit `feat: integrate flexible collection batches`.

### Task 6: Documentation, Packaging, And Release

**Files:** Modify `docs/USER_MANUAL.md`, `docs/DEVELOPER_API.md`, `docs/SELF_REVIEW.md`; update sample project and build artifacts.

- [ ] Document CSV/XLSX mapping, relative assets, region types, defaults, overrides, migration, and QA.
- [ ] Run `python -m pytest --cov=app --cov-report=term-missing`.
- [ ] Build the portable executable and Inno Setup installer.
- [ ] Visually verify a flexible mixed-operation sample and the existing Floral Varsity project.
- [ ] Commit `chore: document and package flexible templates` and push `main`.

## Self-Review

- Every operation type, input format, migration rule, recovery behavior, and locked-pixel requirement maps to a task.
- No operation can modify pixels beyond its registered mask.
- Version 1 compatibility is tested before release.
- The plan contains no deferred implementation placeholders.
