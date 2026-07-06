from app.plugins.manager import PluginManager


def test_plugin_manager_rejects_incompatible_plugin() -> None:
    manager = PluginManager(engine_version="1.0.0")

    result = manager.load_manifest(
        {
            "name": "Old Exporter",
            "version": "1.0.0",
            "author": "Test",
            "minimum_engine_version": "2.0.0",
            "capabilities": ["exporter"],
        }
    )

    assert result.accepted is False
    assert "requires engine" in result.reason


def test_plugin_manager_accepts_compatible_plugin() -> None:
    manager = PluginManager(engine_version="1.2.0")

    result = manager.load_manifest(
        {
            "name": "QA Pack",
            "version": "1.0.0",
            "author": "Test",
            "minimum_engine_version": "1.0.0",
            "capabilities": ["qa"],
        }
    )

    assert result.accepted is True
