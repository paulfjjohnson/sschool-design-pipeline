# School Design Pipeline Design

## Purpose

School Design Pipeline is a native Windows desktop production application for deterministic school apparel artwork generation from locked master templates. It edits only registered regions of existing artwork and never recreates, reinterprets, or prompt-generates artwork.

The first production target is the Floral Varsity school design: large initials, floral fill colors, outline colors, and a straight script school name over a transparent background.

## Non-Negotiable Rules

- The master template is immutable.
- Only registered editable regions may change.
- Locked pixels, geometry, transparency, spacing, layer order, and baseline constraints must be preserved.
- Fonts must not be silently substituted.
- Mascots must not be added unless a future template explicitly registers mascot regions.
- QA must run before export and failures block export.
- Each valid school exports one transparent PNG with 300 DPI metadata.
- `progress.json`, logs, QA results, and reports must be updated throughout processing.
- Completed rows are not regenerated unless the user explicitly reprocesses them.

## Architecture

The application is split into focused modules under `app/`:

- `app/ui`: PySide6 windows, widgets, dialogs, preview views, and models. UI displays state but performs no business logic or image manipulation.
- `app/controller`: `ApplicationController` coordinates project, queue, batch processing, pause/resume/stop, logging, QA, and export.
- `app/data`: dataclasses and serializers for projects, schools, templates, progress, QA results, colors, and settings.
- `app/engine`: deterministic editing services: CSV import, initials, typography, color mapping, template registration, PNG/SVG template editing, and region masking.
- `app/qa`: QA rule library and golden-master/locked-region validators.
- `app/export`: PNG export, filename generation, metadata verification, thumbnails where configured, and report artifacts.
- `app/plugins`: plugin interfaces and discovery for future template engines, exporters, QA providers, color libraries, font providers, and reports.
- `app/utils`: logging setup, filesystem helpers, checksums, error types, retry helpers, and small shared utilities.

All dependencies flow inward through interfaces. The UI depends on the controller, the controller depends on service interfaces, and services operate on serializable dataclasses.

## Data Model

Core objects follow the specification:

- `Project`: project identity, paths, template reference, settings, state, timestamps.
- `SchoolRecord`: row number, school, mascot, primary/secondary colors, generated or overridden initials, filename, status, QA status, notes.
- `Template`: template ID, name, version, format, editable regions, geometry checksum, output profile, default fonts.
- `EditableRegion`: region ID, name, type, bounding box, rotation, lock state, mask path or vector selector.
- `ColorDefinition`: display name, HEX/RGB values, aliases, optional CMYK.
- `Progress`: current index, completed rows, failed rows, skipped rows, last processed, elapsed time.
- `QAResult`: pass/fail, warnings, failures, individual rule outcomes, export metadata.
- `LogEntry`: timestamp, level, module, action, duration, message.

Persistence uses human-readable project JSON, YAML settings, CSV inputs, JSON progress, structured logs, and CSV/HTML reports.

## Template Editing

Version 1 supports:

- PNG raster templates with registered region rectangles and masks.
- SVG templates where deterministic text/color replacement can preserve element transforms, paths, clipping, gradients, and layer order.

Unknown templates enter registration mode. Registration captures metadata, export profile, geometry checksum, editable regions, optional masks, and font requirements.

The PNG engine composites onto a copy of the master template. It renders replacement initials and school script only inside text regions, recolors only pixels inside floral/outline masks, preserves alpha, and validates that no pixel outside editable masks changed. It never writes over the master file.

The SVG engine edits registered elements or groups only. Unsupported SVG constructs fail validation instead of being approximated.

## Batch Pipeline

The batch worker runs off the UI thread:

1. Load project and configuration layers.
2. Validate template, color library, font library, folders, and progress.
3. Import CSV and build a queue.
4. Generate natural initials without padding or invented letters.
5. Normalize colors through the color library.
6. Mark invalid rows `NeedsReview`.
7. For each pending row, edit a working copy of the template.
8. Run QA before export.
9. Export transparent PNG with 300 DPI metadata when QA passes.
10. Save QA result, update `progress.json`, write logs, and continue.
11. Generate final reports.

Pause, resume, stop, skip, and reprocess failed operate through controller-managed batch state. `progress.json` is written after every processed row so forced shutdown can resume at the first incomplete school.

## QA Strategy

QA is mandatory and rule based. Required checks include:

- CSV data presence, initials correctness, color resolution, duplicate filename detection.
- Template identity, template version, geometry checksum, and editable region validity.
- Text content correctness, baseline straightness, and font availability.
- Locked-region pixel integrity, canvas dimensions, transparent alpha, and no unauthorized mascot/artwork insertion.
- PNG format, output path, filename convention, and 300 DPI metadata.

Failures are categorized by severity. Errors block the current row. Critical errors pause the batch. Warnings may allow export while recording review notes.

## UI Design

The PySide6 main window follows the required production layout:

- Menu bar: File, Template, Production, QA, Help.
- Project header: project, template, CSV, output, status.
- Left queue panel: sortable/filterable school records and row actions.
- Center preview: template/current/before-after/checkerboard/QA overlay modes with zoom and pan.
- Right controls panel: Start, Pause, Resume, Stop, Reprocess Failed, Open Output, Export Logs plus batch options.
- QA panel: selected-school rule results.
- Logs panel: live structured log output.
- Status bar: health, progress, current row, elapsed time.

Template registration mode adds region selection tools for initials, script, floral fill, and outline. Freehand artwork editing is not available in version 1.

## Error Handling And Recovery

Errors are classified as configuration, project, template, data, typography, processing, QA, export, or system. User messages include what happened, where it happened, why processing stopped or skipped, and suggested action.

The application preserves completed exports, flushes logs, updates progress, isolates failed rows, and continues or pauses according to user settings. Transient file lock/network-share style failures may be retried. Deterministic failures are not retried automatically.

## Testing

Implementation follows test-first development for core behavior. Coverage focuses on:

- Initial generation and ambiguity handling.
- CSV validation and queue construction.
- Color mapping and unknown-color failures.
- Progress save/resume behavior.
- Template metadata and editable-region validation.
- Locked-region pixel comparison.
- PNG export metadata and alpha preservation.
- Batch integration from sample project to output, QA reports, logs, and progress.

Golden master tests compare canvas, locked pixels, geometry, transparency, editable-region limits, and export metadata.

## Packaging

The release build produces:

- Complete source repository.
- `requirements.txt`.
- Documentation and build instructions.
- Sample project and registered example template.
- PyInstaller portable executable.
- Windows installer build artifacts or reproducible installer instructions.

The application targets Windows 10 and Windows 11 with Python 3.12+ during development.

## Acceptance

The build is complete when a user can open the application, load a master template, load a school CSV, press Start once, walk away, and return to production-ready transparent PNG files for every valid school with QA reports, logs, and resumable project state.
