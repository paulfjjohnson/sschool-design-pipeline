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

Flexible version 2 templates may use CSV or XLSX files and map any column name to an operation. Image columns contain an absolute path or a path relative to the spreadsheet, such as `assets/logo.png`.

## Flexible Templates

Select `Template > Create Flexible Template` to create a new version 2 template directly from a master PNG and optional sample CSV/XLSX file. Add and map operations before saving; no legacy Floral Varsity regions are required.

After loading a template and batch file, select `Template > Edit Template Operations`. Operations can be added, removed, reordered, and mapped to spreadsheet columns. Supported types are `TEXT`, `PATTERN_TEXT`, `SOLID_COLOR`, `PATTERN_FILL`, `IMAGE_REPLACE`, `VISIBILITY`, and `LOCKED`.

Each operation has bounds, a default value, an optional spreadsheet mapping, a required flag, and an override policy. The optional configuration JSON supports settings such as `{"fit":"contain"}`, `{"fit":"cover"}`, `{"case":"title"}`, and `{"color_column":"Accent Color"}`. Saving version 2 operations creates a backup of the prior template metadata.

Use `PATTERN_TEXT` when a spreadsheet value should generate new text and fill that text with a reusable pattern image. For a seersucker mascot design, map the operation column to `Mascot`, set the bounds to the full mascot-word area, and use configuration such as `{"case":"upper","font_path":"C:\\School Designs\\template\\fonts\\Highway.ttf","outline_color_column":"Color 1","pattern_color_column":"Color 2","outline_width":20,"pattern_treatment":"tint_saturated","pattern_scale":0.45}`. Leave the spreadsheet column for the pattern image blank when the template has a shared `pattern.png`; use `pattern_column` only when each row supplies a different pattern file. `pattern_scale` controls pattern size: `1.0` keeps the source tile size, `0.5` makes it half size, and `0.25` makes it one-quarter size.

## Workflow

1. Open the application with `python -m app.main` or the packaged executable.
2. Select `File > New Project` and choose an empty project folder, or select `File > Open Project` and choose its `project.json`.
3. To register new artwork, select `Template > Register Editable Regions`, choose a transparent PNG, choose the exact font files, and choose the script capitalization policy. For best results, choose a separate clean pattern PNG and select either `Preserve Original Colors` or `Tint With Color 2`. Draw `initials` around the full replaceable initials area and `script` around the school-name area. The `floral` selection remains a fallback pattern source when no separate pattern image is supplied. Draw `outline` around a representative outline segment. Press `Save` after all four regions are visible.
4. Alternatively, select `Load Template` to open an existing registered `template.yaml`.
5. Select `Load CSV` and choose a file containing the required columns shown above.
6. Confirm that the project, template, and CSV all appear in the header, then click `Start` once.
7. Leave the workstation while the queue processes. Processing runs in the background, and `Pause`, `Resume`, and `Stop` remain available.
8. Select `Open Output` to review exported PNG files. Reports and resumable state are stored inside the project folder.

The image itself is never modified. Registration copies it to `template/master.png`, creates masks under `template/masks`, and writes `template/template.yaml`.

## Batch Controls

- `Start`: process every pending valid school.
- `Rebuild All`: clear resume state and regenerate every valid school, overwriting matching outputs. Use this after changing a template, pattern selection, fonts, colors, or rendering settings.
- `Pause`: pause processing between rows.
- `Resume`: continue after pause.
- `Stop`: stop after preserving progress.
- `Reprocess Failed`: retry rows after fixing review data.
- `Open Output`: open the project output folder.

## Output

Each successful row produces one transparent PNG with 300 DPI metadata. The filename is derived from the school name and template name.

Batch summaries are written to `reports/batch_summary.csv` and `reports/batch_summary.html`. Failed or review rows are also written to `reports/failed_items.csv` with the row number, school, output filename, and failure reason. Detailed row failures are logged in `logs/school_design_pipeline.log`.

## Safety Rules

- The master template is never overwritten.
- Export is blocked when QA fails.
- Completed rows are not regenerated on resume.
- `progress.json` is saved after each processed row.

