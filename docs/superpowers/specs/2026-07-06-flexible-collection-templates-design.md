# Flexible Collection Templates Design

## Purpose

Replace the Floral Varsity-specific four-region contract with a schema-driven template system that can generate deterministic collections for schools, teams, businesses, events, families, and other batch artwork. The master remains immutable. Only explicitly registered operations may alter output pixels.

## Supported Inputs

Projects accept `.csv` and `.xlsx` batch files. Both importers normalize rows into the same ordered mapping of column names to typed values. CSV remains the portable interchange format; Excel improves operator usability.

Image cells contain absolute paths or paths relative to the spreadsheet directory. Relative paths are recommended, for example `assets/bluff-ridge-logo.png`. Missing, unreadable, unsupported, or unsafe paths mark the row `NeedsReview` before rendering.

## Template Schema

Template schema version 2 stores an ordered list of operations. Every operation has:

- Stable operation ID and operator-facing name.
- Operation type.
- Explicit layer order.
- Registered bounds and optional pixel mask.
- Optional spreadsheet-column mapping.
- Template default value or asset.
- Whether a row value may override the default.
- Type-specific rendering configuration.
- Required/optional status and QA constraints.

The initial operation types are:

- `TEXT`: replace text using registered font, bounds, alignment, case, spacing, rotation, fit policy, fill source, and mapped column.
- `SOLID_COLOR`: recolor registered pixels from a default color or mapped column.
- `PATTERN_FILL`: clip a registered pattern asset into a registered mask or text silhouette; preserve original colors or tint from a mapped color column.
- `IMAGE_REPLACE`: place a default or row-supplied PNG/JPEG inside registered bounds using contain, cover, stretch, or original-size fit.
- `VISIBILITY`: show or hide a registered source element based on a default or mapped boolean column.
- `LOCKED`: explicitly identify immutable reference artwork. All pixels not covered by editable operation masks are implicitly locked.

Defaults and row overrides are independent. A template may use only defaults, only spreadsheet values, or a default with permitted per-row replacement.

## Registration Workflow

Registration is an operation editor, not a fixed sequence of initials, script, floral, and outline selections.

1. Choose immutable master artwork and output profile.
2. Add, remove, duplicate, rename, and reorder operations.
3. Choose an operation type.
4. Draw bounds or load/create its mask.
5. Select an optional spreadsheet column from a sample CSV/XLSX file.
6. Configure a default, override policy, assets, fonts, fit, case, color, and visibility settings.
7. Preview a selected sample row.
8. Validate and save only when every required operation is complete.

The editor displays large artwork fitted to the viewport and maps selections to full-resolution coordinates. Unsupported configurations fail visibly; no implicit font, asset, color, or operation substitution is allowed.

## Rendering Architecture

The renderer executes immutable operation definitions in ascending layer order. Each operation type has a focused handler implementing a common protocol. Handlers receive the master working copy, resolved row value, operation configuration, and project asset resolver.

Before execution, a resolver converts defaults and mapped values into typed inputs. Resolution failures prevent rendering that row. After execution, QA compares the output with the master outside the union of all editable masks. Handlers cannot expand their effective mask at runtime.

Pattern and image operations use registered assets without generating artwork. Pattern repetition may mirror tiles to reduce seams but must not synthesize content. Image replacement clips strictly to registered bounds/masks and preserves aspect ratio according to the configured fit policy.

## Spreadsheet Mapping

The importer preserves source column names. Registration stores mappings by column name, not column position. A project may remap missing columns when loading a new batch file.

The queue stores normalized row values plus resolved asset paths. Required missing values, invalid booleans, unknown colors, and missing image files are reported per row. Extra spreadsheet columns are retained and may be mapped later.

## Compatibility And Migration

Schema version 1 Floral Varsity templates migrate deterministically to version 2 operations:

- `initials` becomes a `TEXT` operation mapped to generated initials.
- Dedicated `pattern.png` becomes a `PATTERN_FILL` dependency for initials.
- `outline` becomes the text outline color source.
- `script` becomes a `TEXT` operation mapped to `School`.
- Existing fonts, case policy, masks, colors, and layer order are preserved.
- Legacy floral crop metadata remains a fallback pattern asset only when no dedicated pattern exists.

Migration writes a backup before saving. Opening an old project does not mutate its master or outputs. The migrated template receives a new schema version and passes the same locked-pixel QA checks.

## User Interface

The main application keeps project, queue, preview, QA, logs, batch controls, and recovery behavior. Template registration gains an operation list and a type-specific properties panel. Batch import accepts CSV and XLSX. A mapping review appears when required template columns are absent.

`Start` resumes pending work. `Rebuild All` explicitly clears progress and regenerates all valid rows. Template-definition changes invalidate prior completion state only after operator confirmation.

## Error Handling

Errors identify the row, operation, mapped column, source value, and corrective action. Configuration errors block template saving. Row-data errors mark only that row `NeedsReview`. Rendering or QA errors fail only the current row unless stop-on-failure is enabled. Missing external assets never fall back silently.

## Testing

Test-first coverage includes:

- CSV/XLSX normalization parity and column-name mapping.
- Relative and absolute asset resolution.
- Defaults, allowed overrides, prohibited overrides, and missing required values.
- Every operation handler and layer-order composition.
- Text case, font, fitting, outline, and counter preservation.
- Pattern preserve/tint behavior and image fit modes.
- Visibility parsing and locked-pixel integrity.
- Version 1 migration and backup behavior.
- Registration validation and large-image coordinate mapping.
- Resume, Rebuild All, reports, logs, QA, packaging, and mixed-operation system acceptance.

## Acceptance Criteria

The feature is complete when an operator can register a template with any supported combination and number of operations, map CSV/XLSX columns, provide defaults and row image paths, run one batch, and receive QA-approved transparent PNGs without changing any unregistered pixel. Existing Floral Varsity projects must migrate and reproduce their current accepted behavior.
