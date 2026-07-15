"""Static safety and packaging checks for the HACS integration."""

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_manifest_uses_home_assistant_bluetooth() -> None:
    manifest = json.loads((ROOT / "custom_components/c5500xk/manifest.json").read_text())
    assert manifest["dependencies"] == ["bluetooth"]
    assert manifest["bluetooth"] == [{"local_name": "C5500XK*", "connectable": True}]


def test_hacs_integration_has_no_external_collector() -> None:
    assert not (ROOT / "collector").exists()
    assert not (ROOT / "custom_components/c5500xk/api.py").exists()


def test_operational_buttons_default_disabled() -> None:
    source = (ROOT / "custom_components/c5500xk/button.py").read_text()
    assert "_attr_entity_registry_enabled_default = False" in source
    assert "CONF_ENABLE_WRITES" in source
