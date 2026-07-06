from pathlib import Path

from app.engine.assets import AssetResolver


def test_asset_resolver_uses_spreadsheet_directory(tmp_path: Path) -> None:
    sheet = tmp_path / "input" / "rows.csv"
    asset = sheet.parent / "assets" / "logo.png"
    asset.parent.mkdir(parents=True)
    asset.write_bytes(b"png")
    assert AssetResolver().resolve("assets/logo.png", sheet) == asset.resolve()
