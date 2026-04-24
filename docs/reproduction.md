# Reproduction Notes

## Local LLM Assumptions

AgentMark in the paper uses locally hosted open-source models instead of remote SaaS APIs. The public reproduction repository follows the same assumption.

- `Meta` node: `Qwen2.5-72B-Instruct`
- `AMD64 worker` nodes: `Qwen2.5-32B-Instruct`
- `ARM64 worker` nodes: `Llama-3-8B-Instruct`
- `Serving stack`: `vLLM`
- `Access pattern`: OpenAI-compatible HTTP endpoints hosted inside the local or cluster network

Example endpoint layout:

```text
http://meta-node:8000/v1/chat/completions
http://worker-amd64-01:8001/v1/chat/completions
http://worker-arm64-01:8002/v1/chat/completions
```

## Protocol Split

- `HTTP`: data-plane tool calls, local LLM serving, and external API simulation
- `gRPC bidirectional streaming`: control-plane communication between the fault orchestrator and worker nodes

Suggested watermark-related metadata:

- `x-agentmark-prev`
- `x-agentmark-sem`
- `x-agentmark-exec`
- `x-agentmark-infra`

For gRPC control messages, the prototype records:

- `agent_id`
- `workflow_id`
- `rollback_boundary`
- `infra_fingerprint`

## Dataset Mapping

- `Itinerary`: mapped to `data/travel/`, including `data_type1.json`, `data_type2.json`, `data_type3.json`, `skill*.json`, and `travel.db`
- `MMLU`: mapped to the local CSV split under `data/dev`, `data/val`, and `data/test`
- `GSM8K`: referenced as an upstream dependency when not bundled locally
- `MIXED`: constructed by uniformly sampling from `GSM8K`, `MMLU`, and `Itinerary`

## Baseline Mapping

- `Erasure Coding`: transport or block integrity baseline
- `Post Mortem`: retrospective trace baseline
- `Service Mesh`: HTTP or gRPC retry baseline
- `Actor Supervision`: restart-on-crash baseline
- `Agent Heuristic`: self-reflection and retry baseline
- `AgentMark`: cross-layer causal watermarking baseline

## What Minimal Reproduction Demonstrates

- semantic mismatch under an `HTTP 200` response is detected
- causal rollback chooses the last safe execution boundary
- replay reuses committed external effects instead of duplicating them

## What Full Reproduction Bundles

- paper-aligned result tables and figure inputs
- dataset inventory and local presence report
- local LLM backend specification
- baseline comparison summary
- protocol and dependency metadata
