# School Design Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-quality Windows desktop application that deterministically edits registered regions of master apparel artwork templates and batch-exports QA-validated transparent PNGs from school CSV data.

**Architecture:** A PySide6 UI delegates all state changes and processing to controller/services. Core behavior is implemented as testable, serializable dataclasses and deterministic services for projects, CSV, initials, colors, template editing, QA, export, progress, reporting, and plugins. Template editing is conservative: unknown template capabilities fail validation instead of approximating artwork.

**Tech Stack:** Python 3.12+, PySide6, Pillow, OpenCV, NumPy, pandas, PyYAML, CairoSVG, PyInstaller, pytest, pytest-cov.

## Global Constraints

- Windows desktop only: Windows 10 and Windows 11.
- Python 3.12+.
- PySide6 UI.
- Pillow, OpenCV, NumPy, pandas, PyYAML, CairoSVG, PyInstaller.
- The application is not an AI image-generation application.
- The application must never recreate artwork.
- Only registered editable regions may change.
- Master templates are immutable.
- Preserve transparency, geometry, typography, alignment, layer order, spacing, baseline, and locked regions.
- Never curve text unless the template requires it.
- Never substitute fonts silently.
- Never add mascots unless template metadata defines mascot regions.
- Required CSV columns: `School`, `Mascot`, `Color 1`, `Color 2`.
- Export individual transparent PNG files with 300 DPI metadata.
- Run QA before export; QA failures block export.
- Maintain `progress.json`, logs, QA reports, and resumable project state.

---

## File Structure

- Create `app/main.py`: PySide6 entry point.
- Create `app/__init__.py`: package marker and version.
- Create `app/data/models.py`: serializable dataclasses and enums.
- Create `app/data/serialization.py`: JSON/YAML read/write helpers.
- Create `app/utils/errors.py`: typed application exceptions and severity/category enums.
- Create `app/utils/paths.py`: filesystem helpers.
- Create `app/utils/logging.py`: app/project logging setup.
- Create `app/config/defaults.yaml`: default application config.
- Create `app/config/manager.py`: configuration hierarchy and validation.
- Create `app/engine/initials.py`: natural initials generator.
- Create `app/engine/colors.py`: color library and mapper.
- Create `app/engine/csv_importer.py`: CSV validation and queue creation.
- Create `app/engine/templates.py`: template metadata, registration validation, masks, checksums.
- Create `app/engine/typography.py`: deterministic text rendering with explicit fonts.
- Create `app/engine/image_engine.py`: PNG/SVG editing interface and PNG raster engine.
- Create `app/qa/rules.py`: QA rule implementations.
- Create `app/qa/service.py`: QA runner and report model.
- Create `app/export/exporter.py`: PNG export and metadata verification.
- Create `app/export/reports.py`: CSV/HTML batch reports.
- Create `app/controller/project_manager.py`: project create/load/save and backups.
- Create `app/controller/progress.py`: progress lifecycle and resume.
- Create `app/controller/batch.py`: worker-thread-safe batch processor.
- Create `app/controller/app_controller.py`: UI-facing orchestration API.
- Create `app/plugins/api.py`: plugin protocols and metadata.
- Create `app/plugins/manager.py`: plugin discovery and registration.
- Create `app/ui/main_window.py`: main PySide6 window layout.
- Create `app/ui/models.py`: Qt table/log/QA models.
- Create `app/ui/preview.py`: image preview with zoom, pan, checkerboard, regions.
- Create `app/ui/registration.py`: region registration dialog.
- Create `app/ui/settings.py`: settings dialog.
- Create `tests/`: unit, integration, golden, resume, and UI-smoke tests.
- Create `sample_project/`: deterministic template, masks, CSV, color library, settings, expected behavior.
- Create `docs/`: user manual, admin guide, developer API, build instructions, traceability matrix, self-review.
- Create `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, `pytest.ini`, `SchoolDesignPipeline.spec`, `scripts/build.ps1`.

---

### Task 1: Repository Foundation, Models, Config, And Logging

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `pytest.ini`
- Create: `app/__init__.py`
- Create: `app/data/models.py`
- Create: `app/data/serialization.py`
- Create: `app/utils/errors.py`
- Create: `app/utils/paths.py`
- Create: `app/utils/logging.py`
- Create: `app/config/defaults.yaml`
- Create: `app/config/manager.py`
- Test: `tests/unit/test_models_serialization.py`
- Test: `tests/unit/test_config_manager.py`
- Test: `tests/unit/test_logging_setup.py`

**Interfaces:**
- Produces: `Project`, `SchoolRecord`, `Template`, `EditableRegion`, `ColorDefinition`, `Progress`, `QAResult`, `AppSettings`, `ProjectSettings`.
- Produces: `read_json(path: Path, model: type[T]) -> T`, `write_json(path: Path, value: Any) -> None`, `read_yaml(path: Path) -> dict[str, Any]`, `write_yaml(path: Path, value: Mapping[str, Any]) -> None`.
- Produces: `ConfigurationManager.load() -> AppSettings`.
- Produces: `configure_logging(log_dir: Path, level: str) -> logging.Logger`.

- [ ] **Step 1: Write failing serialization/config/logging tests**

```python
def test_project_round_trips_json(tmp_path):
    project = Project.new(project_name="Ascension Primary", root_path=tmp_path)
    path = tmp_path / "project.json"
    write_json(path, project)
    loaded = read_json(path, Project)
    assert loaded.project_id == project.project_id
    assert loaded.project_name == "Ascension Primary"

def test_configuration_defaults_load():
    settings = ConfigurationManager(defaults_path=Path("app/config/defaults.yaml")).load()
    assert settings.default_dpi == 300
    assert settings.export_format == "PNG"

def test_project_logger_writes_structured_file(tmp_path):
    logger = configure_logging(tmp_path, "INFO")
    logger.info("startup")
    assert (tmp_path / "school_design_pipeline.log").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/unit/test_models_serialization.py tests/unit/test_config_manager.py tests/unit/test_logging_setup.py -v`

Expected: FAIL because modules are missing.

- [ ] **Step 3: Implement minimal dataclasses, serializers, config manager, and logging setup**

Implement schema-versioned dataclasses, enums, JSON/YAML helpers, path validation, and rotating project logs.

- [ ] **Step 4: Run GREEN**

Run: `pytest tests/unit/test_models_serialization.py tests/unit/test_config_manager.py tests/unit/test_logging_setup.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt requirements-dev.txt pytest.ini app tests
git commit -m "feat: add project foundation and configuration"
```

---

### Task 2: Initials, Colors, CSV Import, And Queue Creation

**Files:**
- Create: `app/engine/initials.py`
- Create: `app/engine/colors.py`
- Create: `app/engine/csv_importer.py`
- Create: `sample_project/input/schools.csv`
- Create: `sample_project/color_library.yaml`
- Test: `tests/unit/test_initials.py`
- Test: `tests/unit/test_color_mapper.py`
- Test: `tests/unit/test_csv_importer.py`

**Interfaces:**
- Consumes: `SchoolRecord`, `ColorDefinition`, `SchoolStatus`.
- Produces: `InitialGenerator.generate(school_name: str) -> InitialResult`.
- Produces: `ColorLibrary.resolve(name: str) -> ColorDefinition`.
- Produces: `CsvImporter.import_file(path: Path) -> list[SchoolRecord]`.

- [ ] **Step 1: Write failing tests for initials, color resolution, and CSV validation**

```python
def test_natural_initials_do_not_pad():
    generator = InitialGenerator()
    assert generator.generate("Pecan Grove Primary").initials == "PGP"
    assert generator.generate("Gonzales Primary").initials == "GP"

def test_unknown_color_marks_row_needs_review(tmp_path):
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text("School,Mascot,Color 1,Color 2\nSugar Mill Primary,Eagles,Maroon,Royal\n", encoding="utf-8")
    importer = CsvImporter(ColorLibrary.from_entries([]), InitialGenerator())
    rows = importer.import_file(csv_path)
    assert rows[0].status.value == "NeedsReview"
    assert "not mapped" in rows[0].notes

def test_duplicate_filenames_are_flagged(tmp_path):
    csv_path = tmp_path / "schools.csv"
    csv_path.write_text("School,Mascot,Color 1,Color 2\nCarver Primary,Bears,Red,Royal\nCarver Primary,Cats,Red,Royal\n", encoding="utf-8")
    importer = CsvImporter(ColorLibrary.default(), InitialGenerator())
    rows = importer.import_file(csv_path)
    assert rows[1].status.value == "NeedsReview"
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/unit/test_initials.py tests/unit/test_color_mapper.py tests/unit/test_csv_importer.py -v`

Expected: FAIL because engine modules are missing.

- [ ] **Step 3: Implement initials/color/CSV services**

Implement deterministic initials from word initials, required-column validation, alias-based color lookup, duplicate filename detection, `NeedsReview` rows for invalid data, and sanitized export filenames.

- [ ] **Step 4: Run GREEN**

Run: `pytest tests/unit/test_initials.py tests/unit/test_color_mapper.py tests/unit/test_csv_importer.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/engine tests/unit sample_project
git commit -m "feat: add school CSV queue creation"
```

---

### Task 3: Project Manager, Progress Recovery, And Reports

**Files:**
- Create: `app/controller/project_manager.py`
- Create: `app/controller/progress.py`
- Create: `app/export/reports.py`
- Test: `tests/unit/test_project_manager.py`
- Test: `tests/unit/test_progress.py`
- Test: `tests/unit/test_reports.py`
- Test: `tests/integration/test_resume_project.py`

**Interfaces:**
- Consumes: dataclasses from `app.data.models`.
- Produces: `ProjectManager.create_project(name: str, root: Path) -> Project`.
- Produces: `ProjectManager.load_project(path: Path) -> Project`.
- Produces: `ProgressService.mark_completed(row: SchoolRecord, qa: QAResult) -> None`.
- Produces: `ProgressService.first_incomplete(records: Sequence[SchoolRecord]) -> int`.
- Produces: `ReportWriter.write_batch_summary(project: Project, records: Sequence[SchoolRecord], qa_results: Sequence[QAResult]) -> ReportPaths`.

- [ ] **Step 1: Write failing tests for project save/load, progress resume, and report output**

```python
def test_progress_resumes_at_first_incomplete(tmp_path):
    progress = ProgressService(tmp_path / "progress.json")
    rows = [SchoolRecord.example(row_number=1), SchoolRecord.example(row_number=2)]
    progress.mark_completed(rows[0], QAResult.passed_for(rows[0]))
    assert progress.first_incomplete(rows) == 1

def test_project_manager_creates_portable_structure(tmp_path):
    project = ProjectManager().create_project("Ascension", tmp_path)
    assert (tmp_path / "project.json").exists()
    assert (tmp_path / "progress.json").exists()
    assert (tmp_path / "output").is_dir()
    assert (tmp_path / "qa").is_dir()

def test_batch_summary_writes_csv_and_html(tmp_path):
    paths = ReportWriter(tmp_path).write_batch_summary(Project.example(tmp_path), [], [])
    assert paths.csv.exists()
    assert paths.html.exists()
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/unit/test_project_manager.py tests/unit/test_progress.py tests/unit/test_reports.py tests/integration/test_resume_project.py -v`

Expected: FAIL because services are missing.

- [ ] **Step 3: Implement project/progress/report services**

Implement portable project folders, JSON project/progress persistence, atomic writes, backups, report CSV/HTML, corrupt-progress error handling, and first-incomplete resume logic.

- [ ] **Step 4: Run GREEN**

Run: `pytest tests/unit/test_project_manager.py tests/unit/test_progress.py tests/unit/test_reports.py tests/integration/test_resume_project.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/controller app/export tests
git commit -m "feat: add project persistence and resume"
```

---

### Task 4: Template Registration, Typography, PNG Engine, Export, And QA

**Files:**
- Create: `app/engine/templates.py`
- Create: `app/engine/typography.py`
- Create: `app/engine/image_engine.py`
- Create: `app/qa/rules.py`
- Create: `app/qa/service.py`
- Create: `app/export/exporter.py`
- Create: `sample_project/template/master.png`
- Create: `sample_project/template/template.yaml`
- Create: `sample_project/template/masks/initials.png`
- Create: `sample_project/template/masks/script.png`
- Create: `sample_project/template/masks/floral.png`
- Create: `sample_project/template/masks/outline.png`
- Test: `tests/unit/test_template_registration.py`
- Test: `tests/unit/test_typography.py`
- Test: `tests/unit/test_image_engine.py`
- Test: `tests/unit/test_qa_rules.py`
- Test: `tests/unit/test_exporter.py`
- Test: `tests/golden/test_locked_regions.py`

**Interfaces:**
- Consumes: `Template`, `EditableRegion`, `SchoolRecord`, `ColorDefinition`, `QAResult`.
- Produces: `TemplateRegistry.load(path: Path) -> Template`.
- Produces: `TemplateValidator.validate(template: Template) -> ValidationResult`.
- Produces: `PngTemplateEngine.render(template: Template, record: SchoolRecord) -> RenderResult`.
- Produces: `QAService.validate(render: RenderResult, record: SchoolRecord) -> QAResult`.
- Produces: `PngExporter.export(render: RenderResult, record: SchoolRecord, output_dir: Path) -> Path`.

- [ ] **Step 1: Write failing tests for template validation, locked-region integrity, QA blocking, and PNG metadata**

```python
def test_template_requires_all_registered_regions(sample_template_path):
    template = TemplateRegistry.load(sample_template_path)
    result = TemplateValidator().validate(template)
    assert result.passed
    assert {r.name for r in template.editable_regions} == {"initials", "script", "floral", "outline"}

def test_render_changes_only_registered_regions(sample_template, sample_school):
    render = PngTemplateEngine().render(sample_template, sample_school)
    assert LockedRegionComparator(sample_template).unexpected_changed_pixels(render.image) == 0

def test_qa_failure_blocks_export(tmp_path, sample_render, sample_school):
    qa = QAResult.failed_for(sample_school, "geometry", "Geometry checksum mismatch")
    with pytest.raises(QABlockedExportError):
        PngExporter().export(sample_render, sample_school, tmp_path, qa)

def test_png_export_has_alpha_and_300_dpi(tmp_path, sample_render, sample_school):
    qa = QAResult.passed_for(sample_school)
    path = PngExporter().export(sample_render, sample_school, tmp_path, qa)
    image = Image.open(path)
    assert image.mode == "RGBA"
    assert image.info["dpi"] == (300, 300)
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/unit/test_template_registration.py tests/unit/test_typography.py tests/unit/test_image_engine.py tests/unit/test_qa_rules.py tests/unit/test_exporter.py tests/golden/test_locked_regions.py -v`

Expected: FAIL because template/image/QA/export modules are missing.

- [ ] **Step 3: Implement template, typography, PNG editing, QA, and export**

Implement mask loading, geometry checksums, region validation, explicit-font text rendering, conservative recolor inside masks, alpha preservation, locked-pixel comparison, required QA rules, PNG save with DPI metadata, and export blocking when QA fails.

- [ ] **Step 4: Run GREEN**

Run: `pytest tests/unit/test_template_registration.py tests/unit/test_typography.py tests/unit/test_image_engine.py tests/unit/test_qa_rules.py tests/unit/test_exporter.py tests/golden/test_locked_regions.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/engine app/qa app/export sample_project tests
git commit -m "feat: add deterministic template editing and QA"
```

---

### Task 5: Batch Controller, Plugin Interfaces, And Integration Pipeline

**Files:**
- Create: `app/controller/batch.py`
- Create: `app/controller/app_controller.py`
- Create: `app/plugins/api.py`
- Create: `app/plugins/manager.py`
- Test: `tests/unit/test_plugin_manager.py`
- Test: `tests/integration/test_batch_pipeline.py`
- Test: `tests/integration/test_reprocess_failed.py`

**Interfaces:**
- Consumes: services from Tasks 1-4.
- Produces: `BatchProcessor.start(project: Project, queue: list[SchoolRecord]) -> BatchResult`.
- Produces: `BatchProcessor.pause() -> None`, `resume() -> None`, `stop() -> None`, `reprocess_failed() -> BatchResult`.
- Produces: `ApplicationController.load_template(path: Path)`, `load_csv(path: Path)`, `start_batch()`.
- Produces: plugin protocols: `TemplateEnginePlugin`, `ExporterPlugin`, `QAPlugin`, `ColorLibraryPlugin`, `FontProviderPlugin`, `ReportPlugin`.

- [ ] **Step 1: Write failing batch and plugin tests**

```python
def test_batch_processes_valid_rows_and_writes_progress(sample_project):
    result = BatchProcessor.default().start(sample_project, sample_project.records)
    assert result.completed == len(sample_project.valid_records)
    assert sample_project.progress_path.exists()
    assert any(sample_project.output_path.glob("*.png"))

def test_completed_rows_are_not_regenerated_on_resume(sample_project):
    processor = BatchProcessor.default()
    first = processor.start(sample_project, sample_project.records[:1])
    second = processor.start(sample_project, sample_project.records)
    assert second.skipped_completed >= 1

def test_plugin_manager_rejects_incompatible_plugin(tmp_path):
    manager = PluginManager(engine_version="1.0.0")
    assert manager.load_manifest({"name": "Old Exporter", "minimum_engine_version": "2.0.0"}).accepted is False
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/unit/test_plugin_manager.py tests/integration/test_batch_pipeline.py tests/integration/test_reprocess_failed.py -v`

Expected: FAIL because controller/plugin modules are missing.

- [ ] **Step 3: Implement batch, controller, and plugin contracts**

Implement dependency-injected services, batch state machine, pause/resume/stop events, progress updates after each row, failure categorization, report generation at completion, and plugin manifest validation.

- [ ] **Step 4: Run GREEN**

Run: `pytest tests/unit/test_plugin_manager.py tests/integration/test_batch_pipeline.py tests/integration/test_reprocess_failed.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/controller app/plugins tests
git commit -m "feat: add batch orchestration and plugins"
```

---

### Task 6: PySide6 Desktop UI

**Files:**
- Create: `app/main.py`
- Create: `app/ui/main_window.py`
- Create: `app/ui/models.py`
- Create: `app/ui/preview.py`
- Create: `app/ui/registration.py`
- Create: `app/ui/settings.py`
- Test: `tests/ui/test_main_window_smoke.py`
- Test: `tests/ui/test_queue_model.py`

**Interfaces:**
- Consumes: `ApplicationController`.
- Produces: runnable app with required menus, header, queue, preview, QA panel, logs, controls, settings, and registration dialog.

- [ ] **Step 1: Write failing UI smoke/model tests**

```python
def test_main_window_contains_required_actions(qtbot):
    window = MainWindow(ApplicationController.fake())
    qtbot.addWidget(window)
    assert window.findChild(QAction, "action_start_batch") is not None
    assert window.findChild(QAction, "action_load_template") is not None

def test_queue_model_exposes_required_columns():
    model = SchoolQueueModel([SchoolRecord.example(row_number=1)])
    assert model.headerData(0, Qt.Horizontal) == "Status"
    assert model.headerData(2, Qt.Horizontal) == "School"
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/ui/test_main_window_smoke.py tests/ui/test_queue_model.py -v`

Expected: FAIL because UI modules are missing.

- [ ] **Step 3: Implement UI**

Implement menu actions, project header, queue table, preview, QA/log tabs, batch controls, settings dialog, template registration dialog, controller signal wiring, and nonblocking worker integration.

- [ ] **Step 4: Run GREEN**

Run: `pytest tests/ui/test_main_window_smoke.py tests/ui/test_queue_model.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add app/ui app/main.py tests/ui
git commit -m "feat: add PySide6 production UI"
```

---

### Task 7: Documentation, Build, Installer, And Acceptance Self-Review

**Files:**
- Create: `docs/USER_MANUAL.md`
- Create: `docs/ADMINISTRATOR_GUIDE.md`
- Create: `docs/DEVELOPER_API.md`
- Create: `docs/BUILD.md`
- Create: `docs/TRACEABILITY.md`
- Create: `docs/SELF_REVIEW.md`
- Create: `SchoolDesignPipeline.spec`
- Create: `scripts/build.ps1`
- Test: `tests/system/test_sample_project_acceptance.py`

**Interfaces:**
- Consumes: all modules.
- Produces: source repo, docs, sample project, build instructions, portable EXE, installer instructions/artifacts, acceptance report.

- [ ] **Step 1: Write failing system acceptance test**

```python
def test_sample_project_one_start_produces_outputs_reports_logs_and_progress(tmp_path):
    project = copy_sample_project(tmp_path)
    result = run_headless_batch(project)
    assert result.failed == 0
    assert list((project.root_path / "output").glob("*.png"))
    assert (project.root_path / "progress.json").exists()
    assert list((project.root_path / "reports").glob("*.html"))
    assert list((project.root_path / "logs").glob("*.log"))
```

- [ ] **Step 2: Run RED**

Run: `pytest tests/system/test_sample_project_acceptance.py -v`

Expected: FAIL until full app pipeline and fixtures are complete.

- [ ] **Step 3: Implement docs, build scripts, PyInstaller spec, and final acceptance workflow**

Document user workflow, administration, plugin/API contracts, build steps, packaging, sample project, known v1 limitations, and self-review. Add PyInstaller spec and PowerShell build script. Run package build on Windows.

- [ ] **Step 4: Run full verification**

Run:

```powershell
pytest --cov=app --cov-report=term-missing
python -m app.main --version
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

Expected: tests pass, app reports version, portable EXE is built.

- [ ] **Step 5: Commit**

```bash
git add docs scripts SchoolDesignPipeline.spec tests/system
git commit -m "chore: add packaging docs and acceptance review"
```

---

## Self-Review

- Spec coverage: Tasks cover native Windows desktop UI, deterministic registered-region editing, CSV import, natural initials, color mapping, project/progress recovery, QA-gated export, reports, logs, plugin interfaces, tests, sample project, and packaging.
- Scope control: PSD/AI/PDF/EPS editing remains future roadmap per spec; v1 implements PNG and conservative SVG support where deterministic.
- Completion scan: This plan contains no unresolved blanks or unassigned implementation tasks.
- Type consistency: The same service names are used across tasks: `ProjectManager`, `ProgressService`, `CsvImporter`, `InitialGenerator`, `ColorLibrary`, `PngTemplateEngine`, `QAService`, `PngExporter`, `BatchProcessor`, `ApplicationController`.

## Execution Choice

Inline execution is selected for this repository because the user explicitly requested continued implementation and routine architectural decisions should not block progress. Before implementation begins, check isolation with `superpowers:using-git-worktrees`; if no isolated worktree exists and the user does not want one, execute in place.
