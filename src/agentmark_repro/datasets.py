from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def inventory_datasets(data_dir: Path) -> dict[str, Any]:
    inventory = {
        "travel": [str(p.name) for p in (data_dir / "travel").glob("*.json")],
        "mathqa": [str(p.name) for p in (data_dir / "MathQA").glob("*.json")],
        "auxiliary_train": [str(p.name) for p in (data_dir / "auxiliary_train").glob("*.csv")],
        "dev": [str(p.name) for p in (data_dir / "dev").glob("*.csv")],
        "test": [str(p.name) for p in (data_dir / "test").glob("*.csv")],
        "val": [str(p.name) for p in (data_dir / "val").glob("*.csv")],
    }
    return inventory

def build_mixed_manifest(data_dir: Path, output_path: Path | None = None) -> list[dict[str, Any]]:
    # Mocking the building of a mixed dataset from the existing sources.
    # The paper mentions MIXED is a mixture of GSM8K, MMLU, and Itinerary.
    manifest = [
        {"source": "GSM8K", "sample_count": 100},
        {"source": "MMLU", "sample_count": 100},
        {"source": "Itinerary", "sample_count": 100},
    ]
    if output_path is None:
        output_path = data_dir / "mixed_manifest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
