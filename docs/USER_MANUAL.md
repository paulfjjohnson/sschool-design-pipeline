# User Manual

## Purpose

School Design Pipeline creates production PNG artwork from registered master templates and a school CSV. It never creates original artwork and never changes locked areas of the master template.

## CSV Format

Required columns:

```csv
School,Mascot,Color 1,Color 2
Pecan Grove Primary,Pelicans,Red,Royal
```

Rows with missing data, unknown colors, duplicate output filenames, or ambiguous initials are marked for review and are not exported.

## Workflow

1. Open the application with `python -m app.main` or the packaged executable.
2. Create or open a project.
3. Load a registered template metadata file such as `sample_project/template/template.yaml`.
4. Load a school CSV such as `sample_project/input/schools.csv`.
5. Click `Start Batch`.
6. Leave the workstation while the queue processes.
7. Review the output folder, logs, QA results, progress file, and reports.

## Batch Controls

- `Start`: process every pending valid school.
- `Pause`: pause processing between rows.
- `Resume`: continue after pause.
- `Stop`: stop after preserving progress.
- `Reprocess Failed`: retry rows after fixing review data.
- `Open Output`: open the project output folder.

## Output

Each successful row produces one transparent PNG with 300 DPI metadata. The filename is derived from the school name and template name.

## Safety Rules

- The master template is never overwritten.
- Export is blocked when QA fails.
- Completed rows are not regenerated on resume.
- `progress.json` is saved after each processed row.

