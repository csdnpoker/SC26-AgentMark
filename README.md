# AgentMark

AgentMark is a local reproducibility-oriented prototype for the paper's artifact description and evaluation workflow. This repository is organized to support two paths:

- `minimal reproduction`: validates the core mechanism claims, including semantic fault interception, causal rollback, and exactly-once protection for committed side-effects.
- `full reproduction`: regenerates the paper's main result bundles, figures, and tables from structured experiment data and deterministic simulation logic.

This repository is designed as a clean public-facing codebase extracted from the paper workspace. It does not depend on the surrounding manuscript files.

## Paper Alignment

- `Local LLMs`: the paper assumes locally hosted open-source models rather than remote SaaS APIs. This repository therefore documents `Qwen2.5-72B`, `Qwen2.5-32B`, and `Llama-3-8B-Instruct` as local vLLM-served backends.
- `Protocols`: HTTP is used for tool calls and OpenAI-compatible local LLM endpoints, while gRPC bidirectional streaming is used for the control plane between the orchestrator and worker nodes.
- `Datasets`: `Itinerary` is mapped to the local `data/travel/` folder, and `MIXED` is treated as a uniform mixture of `GSM8K`, `MMLU`, and `Itinerary`.
- `Baselines`: the repository includes structured definitions for `Erasure Coding`, `Post Mortem`, `Service Mesh`, `Actor Supervision`, `Agent Heuristic`, and `AgentMark`.

## What This Repository Reproduces

- `RQ1`: mixed-fault robustness metrics, including `TCR` and `FDR`
- `RQ1 complement`: application-level task quality table
- `RQ2`: duplicate side-effect rate and `MTTR`
- `RQ3`: heterogeneous failover outcome summary
- `RQ4`: overhead, communication cost, and scalability plots
- a minimal workflow run that demonstrates the AgentMark mechanism

## Repository Layout

```text
agentmark/
  data/              # local benchmark assets already available in the workspace
  src/agentmark_repro/
    data.py          # structured paper metrics, backends, datasets, protocols
    datasets.py      # dataset inventory and MIXED manifest generation
    baselines.py     # baseline definitions and scenario summaries
    core.py          # watermarking, ledger, and minimal workflow simulation
    plots.py         # figure and table regeneration
  docs/
    reproduction.md  # local deployment and protocol notes
    sources.md       # versions, URLs, and dataset provenance
  scripts/
    run_minimal.py   # mechanism-oriented validation
    run_full.py      # result bundle and figure generation
  tests/
    test_repro.py    # focused regression tests
  outputs/           # generated results
```


## Local LLM Serving

- `Meta node`: `Qwen2.5-72B-Instruct` served locally with `vLLM`
- `AMD64 workers`: `Qwen2.5-32B-Instruct` served locally with `vLLM`
- `ARM64 workers`: `Llama-3-8B-Instruct` served locally with `vLLM`
- `Endpoint style`: OpenAI-compatible HTTP endpoints such as `http://<host>:8000/v1/chat/completions`
- `Control plane`: orchestrator-to-worker communication modeled as gRPC bidirectional streams

## Datasets

- `MMLU`: local CSV split already present under `data/`
- `Itinerary`: local JSON task files and `travel.db` are present under `data/travel/`
- `GSM8K`: not bundled in this prototype; fetch from the upstream repository listed in `docs/sources.md`
- `MIXED`: generated as a manifest that uniformly mixes `GSM8K`, `MMLU`, and `Itinerary`

## Outputs

- `outputs/minimal/minimal_summary.json`: mechanism-level validation summary
- `outputs/full/full_results.json`: full structured result bundle
- `outputs/full/figures/`: regenerated figures and CSV tables
- `data/mixed_manifest.json`: generated source manifest for the `MIXED` benchmark



### Minimal Reproduction

Minimal reproduction is meant to answer: "Does the mechanism work as claimed?"

Expected checks:

- semantic watermark mismatch is detected before silent propagation
- a causally valid rollback boundary is identified
- committed side-effects are not duplicated during replay


## Notes

- This repository currently provides a reproducibility prototype rather than a production-grade distributed deployment.
- The figure-generation code is grounded in the metrics reported in the paper and is organized so the outputs can be regenerated from structured inputs.
- If you later decide to connect a real multi-node runtime, `src/agentmark_repro/core.py` is the right place to extend the ledger and runtime integration.
- Version references, upstream URLs, and dataset provenance are summarized in `docs/sources.md`.
- Local execution assumptions, protocol roles, and baseline mappings are summarized in `docs/reproduction.md`.
