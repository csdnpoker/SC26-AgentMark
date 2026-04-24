from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agentmark_repro.baselines import simulate_baseline_scenarios  # noqa: E402
from agentmark_repro.core import AgentMarkRuntime, semantic_watermark  # noqa: E402
from agentmark_repro.datasets import build_mixed_manifest, inventory_datasets  # noqa: E402


def test_semantic_watermark_changes_with_schema() -> None:
    good = {"api": "flight_search", "currency": "USD"}
    bad = {"api": "flight_search", "amount": 7800, "currency": "JPY"}
    assert semantic_watermark(good) != semantic_watermark(bad)


def test_minimal_runtime_detects_fault_and_preserves_effects() -> None:
    runtime = AgentMarkRuntime()
    result = runtime.run_minimal_workflow()
    assert result.semantic_fault_detected is True
    assert result.causal_rollback_used is True
    assert result.duplicate_side_effects == 0


def test_replay_demo_uses_cached_effects_without_duplicates() -> None:
    runtime = AgentMarkRuntime()
    result = runtime.run_exactly_once_replay_demo()
    assert result.crash_detected is True
    assert result.causal_rollback_used is True
    assert result.duplicate_side_effects == 0
    assert "flight-booking-1" in result.committed_effects


def test_dataset_inventory_finds_itinerary_and_mmlu_assets() -> None:
    inventory = inventory_datasets(ROOT)
    assert inventory["local_presence"]["Itinerary"]["sqlite_db_present"] is True
    assert inventory["local_presence"]["MMLU"]["test_csv_files"] > 0


def test_mixed_manifest_is_generated_locally() -> None:
    manifest = build_mixed_manifest(ROOT, sample_per_dataset=4)
    assert manifest["construction_rule"] == "uniform_sample"
    assert "Itinerary" in manifest["sources"]


def test_baseline_simulation_captures_protocol_specific_limits() -> None:
    scenarios = simulate_baseline_scenarios()
    assert scenarios["semantic_http_200_fault"]["Service Mesh"]["detected"] is False
    assert scenarios["grpc_failover_under_gray_failure"]["AgentMark"]["heterogeneous_failover"] is True
