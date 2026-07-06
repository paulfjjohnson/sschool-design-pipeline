$ErrorActionPreference = "Stop"

Write-Host "Running tests..."
python -m pytest

Write-Host "Building portable executable..."
python -m PyInstaller --clean --noconfirm SchoolDesignPipeline.spec

$exe = Join-Path $PSScriptRoot "..\dist\SchoolDesignPipeline\SchoolDesignPipeline.exe"
if (!(Test-Path $exe)) {
    throw "Build failed: $exe was not created."
}

Write-Host "Built $exe"

