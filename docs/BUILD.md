# Build Instructions

## Source Setup

```powershell
python --version
python -m pip install -r requirements-dev.txt
python -m pytest
```

Python must be 3.12 or newer.

## Run The App

```powershell
python -m app.main
```

Version check:

```powershell
python -m app.main --version
```

## Portable EXE

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

Output:

```text
dist/SchoolDesignPipeline/SchoolDesignPipeline.exe
```

## Installer

Install Inno Setup, then compile:

```powershell
iscc installer/SchoolDesignPipeline.iss
```

The installer script expects the portable build to exist in `dist/SchoolDesignPipeline/`.

