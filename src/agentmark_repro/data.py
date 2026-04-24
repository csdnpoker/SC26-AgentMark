from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass
class PlatformNode:
    name: str
    role: str
    cpu_arch: str
    gpu: str
    vllm_model: str

PLATFORM_SETTINGS = [
    PlatformNode("Orchestrator", "Control Plane", "amd64", "None", "Qwen2.5-32B"),
    PlatformNode("Worker-1", "Execution Node", "amd64", "A100", "Qwen2.5-72B"),
    PlatformNode("Worker-2", "Execution Node", "arm64", "T4G", "Llama-3-8B-Instruct"),
]

@dataclass
class ProtocolSpec:
    name: str
    usage: str
    metadata_fields: tuple[str, ...]

PROTOCOL_SPECS = [
    ProtocolSpec("HTTP", "Tool calls and OpenAI-compatible local LLM endpoints", ()),
    ProtocolSpec("gRPC", "Fault orchestrator to worker coordination, recovery directives, and ledger subscription events", ("agent_id", "workflow_id", "rollback_boundary", "infra_fingerprint")),
]

@dataclass
class BaselineSpec:
    name: str
    recovery_behavior: str
    limitation: str

BASELINE_SPECS = [
    BaselineSpec("Erasure Coding", "Redundant task execution across multiple nodes.", "High overhead and does not prevent duplicate side effects."),
    BaselineSpec("Post Mortem", "Log analysis after failure.", "No real-time recovery."),
    BaselineSpec("Service Mesh", "Network-level retries.", "Cannot handle semantic application faults."),
    BaselineSpec("Actor Supervision", "Pod restarts via liveness probes.", "Loses agent memory context on restart."),
    BaselineSpec("Agent Heuristic", "LLM-driven reflection and retry.", "Slow and prone to hallucination loops."),
    BaselineSpec("AgentMark", "Causal ledger with heterogeneous failover.", "None."),
]

@dataclass
class DependencySpec:
    name: str
    version: str
    url: str

DEPENDENCY_SPECS = [
    DependencySpec("vLLM", "0.4.0+", "https://github.com/vllm-project/vllm"),
    DependencySpec("LangChain", "0.3.x", "https://github.com/langchain-ai/langchain"),
    DependencySpec("AgentScope", "0.1.x", "https://github.com/modelscope/agentscope"),
]

@dataclass
class DatasetSpec:
    name: str
    source: str
    path: str
    components: list[str]

DATASET_SPECS = [
    DatasetSpec("Itinerary", "local", "data/travel/", []),
    DatasetSpec("MIXED", "generated", "", ["GSM8K", "MMLU", "Itinerary"]),
]

@dataclass
class LocalLLMBackend:
    model: str
    backend: str
    quantization: str

LOCAL_LLM_BACKENDS = [
    LocalLLMBackend("Qwen2.5-72B", "vLLM", "AWQ"),
    LocalLLMBackend("Qwen2.5-32B", "vLLM", "None"),
    LocalLLMBackend("Llama-3-8B-Instruct", "vLLM", "None"),
]

APPLICATION_QUALITY = {}

RQ1_MIXED_FAULTS = {
    "methods": ["Erasure Coding", "Post Mortem", "Service Mesh", "Actor Supervision", "Agent Heuristic", "AgentMark"],
    "fdr": [0.0, 0.0, 12.5, 45.0, 68.2, 98.7],
    "tcr": [34.2, 34.2, 34.5, 41.0, 52.3, 96.5],
}

RQ2_RECOVERY = {
    "methods": ["Erasure Coding", "Post Mortem", "Service Mesh", "Actor Supervision", "Agent Heuristic", "AgentMark"],
    "duplicate_side_effect_rate": [100.0, 100.0, 100.0, 100.0, 100.0, 0.0],
    "mttr_seconds": [0.0, 0.0, 0.0, 22.5, 25.0, 1.4],
}

RQ3_HETEROGENEOUS_FAILOVER = {}

RQ4_OVERHEAD = {
    "payload_latency_ms": {
        "payload_sizes": ["1KB", "10KB", "100KB", "1MB", "10MB"],
        "vanilla_rpc": [2.5, 4.8, 12.5, 45.0, 250.0],
        "agentmark_rpc": [8.5, 11.2, 18.5, 58.0, 280.0],
    },
    "per_step_latency_ms": {
        "Erasure Coding": 150,
        "Post Mortem": 120,
        "Service Mesh": 130,
        "Actor Supervision": 140,
        "Agent Heuristic": 800,
        "AgentMark": 160,
    }
}

MINIMAL_REPRODUCTION_EXPECTATIONS = {
    "semantic_fault_detected": True,
    "causal_rollback_used": True,
    "duplicate_side_effects": 0
}
