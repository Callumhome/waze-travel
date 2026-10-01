import json
from pathlib import Path


def test_manifest():
    manifest = json.loads(
        Path("custom_components/waze_travel/manifest.json").read_text()
    )

    assert manifest["domain"] == "waze_travel"
    assert manifest["version"] == "0.1.3"
    assert "pywaze==1.2.3" in manifest["requirements"]
    assert manifest["config_flow"] is True
