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
2. Select `File > New Project` and choose an empty project folder, or select `File > Open Project` and choose its `project.json`.
3. To register new artwork, select `Template > Register Editable Regions`, choose a transparent PNG, then draw the `initials`, `script`, `floral`, and `outline` regions. Select each region name before dragging its rectangle and press `Save` after all four are visible.
4. Alternatively, select `Load Template` to open an existing registered `template.yaml`.
5. Select `Load CSV` and choose a file containing the required columns shown above.
6. Confirm that the project, template, and CSV all appear in the header, then click `Start` once.
7. Leave the workstation while the queue processes. Processing runs in the background, and `Pause`, `Resume`, and `Stop` remain available.
8. Select `Open Output` to review exported PNG files. Reports and resumable state are stored inside the project folder.

The image itself is never modified. Registration copies it to `template/master.png`, creates masks under `template/masks`, and writes `template/template.yaml`.

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

