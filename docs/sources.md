# Sources And Versions

## Core Software

| Component | Suggested Version | Role | URL |
| --- | --- | --- | --- |
| Python | 3.10+ | runtime and experiment scripts | https://www.python.org/downloads/ |
| Redis | 7.x | Causal Ledger backend | https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/ |
| vLLM | 0.6+ | local LLM serving | https://docs.vllm.ai/ |
| LangChain | 0.2+ | workflow integration | https://python.langchain.com/ |
| AgentScope | 0.0.8+ | multi-agent integration | https://github.com/modelscope/agentscope |
| grpcio | 1.66+ | gRPC control plane prototype | https://grpc.io/docs/languages/python/quickstart/ |
| requests | 2.31+ | HTTP fault injection target | https://requests.readthedocs.io/ |
| httpx | 0.27+ | async HTTP fault injection target | https://www.python-httpx.org/ |

## Local Models

| Model | Deployment Form | Notes |
| --- | --- | --- |
| Qwen2.5-72B-Instruct | local vLLM service | meta node controller / planner |
| Qwen2.5-32B-Instruct | local vLLM service | AMD64 worker pool |
| Llama-3-8B-Instruct | local vLLM service | ARM64 worker pool for heterogeneous failover |

## Benchmark Provenance

| Dataset | Local Path | Upstream URL | Notes |
| --- | --- | --- | --- |
| MMLU | `data/` | https://github.com/hendrycks/test | local CSV split is already present |
| GSM8K | not bundled | https://github.com/openai/grade-school-math | fetch separately if needed |
| Itinerary / TravelPlanner-style tasks | `data/travel/` | https://github.com/OSU-NLP-Group/TravelPlanner | local JSON tasks and `travel.db` are used in this repo |
| MIXED | generated | derived from the above | uniform mixture manifest is generated locally |

## Protocol References

| Protocol | Purpose | URL |
| --- | --- | --- |
| HTTP | local LLM and tool endpoints | https://developer.mozilla.org/en-US/docs/Web/HTTP |
| gRPC | control-plane streaming | https://grpc.io/docs/what-is-grpc/introduction/ |

## Paper-Oriented Notes

- The repository keeps the local-LLM assumption from the paper instead of switching to hosted APIs.
- The Itinerary workload is grounded in the local `travel` assets already present in the workspace.
- The MIXED workload is represented as a derived benchmark manifest rather than a separately stored raw dataset.
