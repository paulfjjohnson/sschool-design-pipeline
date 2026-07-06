# School Design Pipeline

School Design Pipeline is a Windows desktop application for deterministic apparel artwork production from locked master templates.

It is not an AI image-generation app. It edits only registered editable regions of an existing template, runs QA, and exports one transparent PNG per valid school row.

## Quick Start

```powershell
python -m pip install -r requirements-dev.txt
python -m app.main
```

Run the test suite:

```powershell
python -m pytest
```

Build the portable executable:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

See [docs/BUILD.md](docs/BUILD.md) and [docs/USER_MANUAL.md](docs/USER_MANUAL.md).

