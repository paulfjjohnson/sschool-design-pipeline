# Developer API

## Core Services

- `ApplicationController`: UI-facing orchestration.
- `ProjectManager`: create, load, and save portable projects.
- `ProgressService`: atomic progress lifecycle and resume detection.
- `CsvImporter`: CSV schema validation and queue creation.
- `InitialGenerator`: deterministic natural school initials.
- `ColorLibrary`: display-name and alias color resolution.
- `TemplateRegistry`: template metadata loading.
- `TemplateValidator`: editable-region and geometry validation.
- `PngTemplateEngine`: deterministic PNG rendering inside registered masks.
- `QAService`: rule-based validation before export.
- `PngExporter`: transparent PNG export with DPI metadata.
- `BatchProcessor`: full queue processing, resume, failed-row reprocess.
- `PluginManager`: manifest compatibility checks.

## Plugin Contracts

Plugin manifest fields:

- `name`
- `version`
- `author`
- `minimum_engine_version`
- `capabilities`

Current capability categories:

- `template`
- `exporter`
- `qa`
- `color-library`
- `font-provider`
- `report`

Plugins requiring a newer engine are rejected during startup.

