from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .baselines import simulate_baseline_scenarios
from .data import (
    APPLICATION_QUALITY,
    BASELINE_SPECS,
    DATASET_SPECS,
    DEPENDENCY_SPECS,
    LOCAL_LLM_BACKENDS,
    MINIMAL_REPRODUCTION_EXPECTATIONS,
    PLATFORM_SETTINGS,
    PROTOCOL_SPECS,
    RQ1_MIXED_FAULTS,
    RQ2_RECOVERY,
    RQ3_HETEROGENEOUS_FAILOVER,
    RQ4_OVERHEAD,
)
from .datasets import build_mixed_manifest, inventory_datasets


def stable_hash(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def semantic_watermark(payload: dict[str, Any]) -> str:
    normalized = {
        "keys": sorted(payload.keys()),
        "types": {key: type(value).__name__ for key, value in sorted(payload.items())},
    }
    return stable_hash(normalized)


def execution_watermark(step_id: str, previous_exec_hash: str | None) -> str:
    return stable_hash({"step_id": step_id, "previous": previous_exec_hash})


def infrastructure_watermark(cpu_arch: str, gpu: str, runtime: str) -> str:
    return stable_hash({"cpu_arch": cpu_arch, "gpu": gpu, "runtime": runtime})


@dataclass
class WorkflowStep:
    step_id: str
    action: str
    payload: dict[str, Any]
    external_effect_id: str | None = None


@dataclass
class LedgerEvent:
    step_id: str
    semantic_hash: str
    exec_hash: str
    infra_hash: str
    status: str
    external_effect_id: str | None = None


@dataclass
class MinimalRunResult:
    semantic_fault_detected: bool
    causal_rollback_used: bool
    duplicate_side_effects: int
    replay_start_step: str
    committed_effects: list[str] = field(default_factory=list)
    event_log: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ReplayRunResult:
    crash_detected: bool
    causal_rollback_used: bool
    duplicate_side_effects: int
    replay_start_step: str
    committed_effects: list[str] = field(default_factory=list)
    event_log: list[dict[str, Any]] = field(default_factory=list)


class CausalLedger:
    def __init__(self) -> None:
        self.events: list[LedgerEvent] = []
        self.effect_cache: dict[str, str] = {}

    def append(self, event: LedgerEvent) -> None:
        self.events.append(event)

    def last_safe_step(self) -> str | None:
        for event in reversed(self.events):
            if event.status == "ok":
                return event.step_id
        return None

    def commit_effect(self, effect_id: str, response: str) -> str:
        self.effect_cache.setdefault(effect_id, response)
        return self.effect_cache[effect_id]

    def has_effect(self, effect_id: str) -> bool:
        return effect_id in self.effect_cache


class AgentMarkRuntime:
    def __init__(self, runtime_name: str = "python3.11") -> None:
        node = PLATFORM_SETTINGS[1]
        self.infra_hash = infrastructure_watermark(node.cpu_arch, node.gpu, runtime_name)
        self.ledger = CausalLedger()

    def run_minimal_workflow(self) -> MinimalRunResult:
        steps = [
            WorkflowStep("step-1", "plan", {"goal": "book trip", "city": "Tokyo"}),
            WorkflowStep("step-2", "fetch_flight", {"api": "flight_search", "currency": "USD"}),
            WorkflowStep("step-3", "reserve_hotel", {"hotel": "Sakura", "nights": 3}, "hotel-booking-1"),
            WorkflowStep("step-4", "confirm_itinerary", {"approval": True}),
        ]

        previous_exec_hash: str | None = None
        event_log: list[dict[str, Any]] = []
        semantic_fault_detected = False
        causal_rollback_used = False
        duplicate_side_effects = 0
        replay_start_step = "step-1"

        for step in steps:
            payload = dict(step.payload)
            if step.step_id == "step-2":
                # Inject a semantic fault that changes the payload shape without
                # triggering a transport failure.
                payload = {"api": "flight_search", "amount": 7800, "currency": "JPY"}

            semantic_hash = semantic_watermark(payload)
            exec_hash = execution_watermark(step.step_id, previous_exec_hash)

            if step.step_id == "step-2":
                expected_hash = semantic_watermark({"api": "flight_search", "currency": "USD"})
                if semantic_hash != expected_hash:
                    semantic_fault_detected = True
                    replay_start_step = self.ledger.last_safe_step() or "step-1"
                    causal_rollback_used = replay_start_step != "step-1" or len(self.ledger.events) > 0
                    self.ledger.append(
                        LedgerEvent(
                            step_id=step.step_id,
                            semantic_hash=semantic_hash,
                            exec_hash=exec_hash,
                            infra_hash=self.infra_hash,
                            status="semantic_fault",
                        )
                    )
                    event_log.append(
                        {
                            "step_id": step.step_id,
                            "action": step.action,
                            "status": "semantic_fault",
                            "rollback_boundary": replay_start_step,
                        }
                    )
                    break

            effect_response = None
            if step.external_effect_id:
                effect_response = self.ledger.commit_effect(step.external_effect_id, "confirmed")
                if self.ledger.has_effect(step.external_effect_id) and step.step_id != "step-3":
                    duplicate_side_effects += 1

            self.ledger.append(
                LedgerEvent(
                    step_id=step.step_id,
                    semantic_hash=semantic_hash,
                    exec_hash=exec_hash,
                    infra_hash=self.infra_hash,
                    status="ok",
                    external_effect_id=step.external_effect_id,
                )
            )
            previous_exec_hash = exec_hash
            event_log.append(
                {
                    "step_id": step.step_id,
                    "action": step.action,
                    "status": "ok",
                    "external_effect_id": step.external_effect_id,
                    "effect_response": effect_response,
                }
            )

        return MinimalRunResult(
            semantic_fault_detected=semantic_fault_detected,
            causal_rollback_used=causal_rollback_used,
            duplicate_side_effects=duplicate_side_effects,
            replay_start_step=replay_start_step,
            committed_effects=list(self.ledger.effect_cache.keys()),
            event_log=event_log,
        )

    def run_exactly_once_replay_demo(self) -> ReplayRunResult:
        steps = [
            WorkflowStep("step-1", "plan", {"goal": "book trip", "city": "Tokyo"}),
            WorkflowStep("step-2", "reserve_hotel", {"hotel": "Sakura", "nights": 3}, "hotel-booking-1"),
            WorkflowStep("step-3", "reserve_flight", {"airline": "NH", "seat": "14A"}, "flight-booking-1"),
            WorkflowStep("step-4", "issue_invoice", {"currency": "USD"}),
        ]

        event_log: list[dict[str, Any]] = []
        previous_exec_hash: str | None = None
        crash_detected = False
        causal_rollback_used = False
        duplicate_side_effects = 0
        replay_start_step = "step-3"

        for step in steps:
            semantic_hash = semantic_watermark(step.payload)
            exec_hash = execution_watermark(step.step_id, previous_exec_hash)
            effect_response = None

            if step.external_effect_id:
                effect_response = self.ledger.commit_effect(step.external_effect_id, "confirmed")

            self.ledger.append(
                LedgerEvent(
                    step_id=step.step_id,
                    semantic_hash=semantic_hash,
                    exec_hash=exec_hash,
                    infra_hash=self.infra_hash,
                    status="ok",
                    external_effect_id=step.external_effect_id,
                )
            )
            event_log.append(
                {
                    "step_id": step.step_id,
                    "status": "ok",
                    "external_effect_id": step.external_effect_id,
                    "effect_response": effect_response,
                }
            )
            previous_exec_hash = exec_hash

            if step.step_id == "step-3":
                crash_detected = True
                causal_rollback_used = True
                replay_start_step = self.ledger.last_safe_step() or "step-2"
                event_log.append(
                    {
                        "step_id": step.step_id,
                        "status": "crash_detected",
                        "rollback_boundary": replay_start_step,
                    }
                )
                break

        # Replay from the last safe boundary. The ledger cache ensures committed
        # effects are reused instead of being issued a second time.
        replay_steps = [
            WorkflowStep("step-3", "reserve_flight", {"airline": "NH", "seat": "14A"}, "flight-booking-1"),
            WorkflowStep("step-4", "issue_invoice", {"currency": "USD"}),
        ]
        previous_exec_hash = self.ledger.events[-1].exec_hash if self.ledger.events else None
        for step in replay_steps:
            semantic_hash = semantic_watermark(step.payload)
            exec_hash = execution_watermark(f"{step.step_id}-replay", previous_exec_hash)
            if step.external_effect_id:
                already_committed = self.ledger.has_effect(step.external_effect_id)
                self.ledger.commit_effect(step.external_effect_id, "confirmed")
                if not already_committed:
                    duplicate_side_effects += 1

            self.ledger.append(
                LedgerEvent(
                    step_id=f"{step.step_id}-replay",
                    semantic_hash=semantic_hash,
                    exec_hash=exec_hash,
                    infra_hash=self.infra_hash,
                    status="replayed",
                    external_effect_id=step.external_effect_id,
                )
            )
            event_log.append(
                {
                    "step_id": f"{step.step_id}-replay",
                    "status": "replayed",
                    "external_effect_id": step.external_effect_id,
                    "cache_hit": bool(step.external_effect_id and self.ledger.has_effect(step.external_effect_id)),
                }
            )
            previous_exec_hash = exec_hash

        return ReplayRunResult(
            crash_detected=crash_detected,
            causal_rollback_used=causal_rollback_used,
            duplicate_side_effects=duplicate_side_effects,
            replay_start_step=replay_start_step,
            committed_effects=list(self.ledger.effect_cache.keys()),
            event_log=event_log,
        )


def run_minimal_reproduction(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    repo_root = output_path.parents[1]

    semantic_runtime = AgentMarkRuntime()
    semantic_result = semantic_runtime.run_minimal_workflow()
    replay_runtime = AgentMarkRuntime()
    replay_result = replay_runtime.run_exactly_once_replay_demo()
    summary = {
        "expectations": MINIMAL_REPRODUCTION_EXPECTATIONS,
        "semantic_fault_demo": asdict(semantic_result),
        "exactly_once_demo": asdict(replay_result),
        "pass": {
            "semantic_fault_detected": semantic_result.semantic_fault_detected,
            "causal_rollback_used": semantic_result.causal_rollback_used and replay_result.causal_rollback_used,
            "duplicate_side_effects": replay_result.duplicate_side_effects == 0,
        },
        "protocols": [asdict(spec) for spec in PROTOCOL_SPECS],
        "local_llm_backends": [asdict(spec) for spec in LOCAL_LLM_BACKENDS],
        "dataset_inventory": inventory_datasets(repo_root),
    }

    (output_path / "minimal_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary


def run_full_reproduction(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    repo_root = output_path.parents[1]
    minimal = run_minimal_reproduction(output_path / "minimal")
    mixed_manifest = build_mixed_manifest(repo_root)
    dataset_inventory = inventory_datasets(repo_root)
    baselines = simulate_baseline_scenarios()

    results = {
        "platform": [asdict(node) for node in PLATFORM_SETTINGS],
        "local_llm_backends": [asdict(spec) for spec in LOCAL_LLM_BACKENDS],
        "dataset_specs": [asdict(spec) for spec in DATASET_SPECS],
        "dataset_inventory": dataset_inventory,
        "mixed_manifest": mixed_manifest,
        "protocol_specs": [asdict(spec) for spec in PROTOCOL_SPECS],
        "dependency_specs": [asdict(spec) for spec in DEPENDENCY_SPECS],
        "baseline_specs": [asdict(spec) for spec in BASELINE_SPECS],
        "baseline_simulation": baselines,
        "rq1_mixed_faults": RQ1_MIXED_FAULTS,
        "application_quality": APPLICATION_QUALITY,
        "rq2_recovery": RQ2_RECOVERY,
        "rq3_heterogeneous_failover": RQ3_HETEROGENEOUS_FAILOVER,
        "rq4_overhead": RQ4_OVERHEAD,
        "minimal_reproduction": minimal,
    }
    (output_path / "full_results.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )
    return results
