# Administrator Guide

## Supported Platforms

- Windows 10
- Windows 11
- Python 3.12+ for source installs

## Project Storage

Projects are self-contained folders with:

- `project.json`
- `settings.yaml`
- `progress.json`
- `template/`
- `input/`
- `output/`
- `logs/`
- `qa/`
- `reports/`
- `backups/`

## Backups And Recovery

The application writes atomic progress updates. If processing is interrupted, reopen the project and resume at the first incomplete school. Completed exports are not regenerated unless explicitly reprocessed.

## Logging

Project logs are written to `logs/school_design_pipeline.log` and rotate automatically. Operational events include startup, batch start/finish, row failures, QA failures, and export events.

## Deployment

Use `scripts/build.ps1` to create a portable executable in `dist/SchoolDesignPipeline/`. If Inno Setup is installed, use `installer/SchoolDesignPipeline.iss` to create a Windows installer.

