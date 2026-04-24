from __future__ import annotations

import json
from pathlib import Path
from typing import Any

class LocalEventStore:
    """Fallback local event store when Redis is unavailable."""
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.events: list[dict[str, Any]] = []

    def append(self, event: dict[str, Any]) -> None:
        self.events.append(event)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def get_all(self) -> list[dict[str, Any]]:
        return self.events

class RedisEventStore:
    """Redis-backed causal ledger stream as described in the paper."""
    def __init__(self, host: str = "localhost", port: int = 6379, stream_key: str = "agentmark:causal_ledger") -> None:
        self.stream_key = stream_key
        try:
            import redis
            self.client = redis.Redis(host=host, port=port, decode_responses=True)
            self.available = self.client.ping()
        except (ImportError, Exception):
            self.client = None
            self.available = False

    def append(self, event: dict[str, Any]) -> None:
        if self.available and self.client:
            try:
                # Redis streams require dict[str, str] mapping
                payload = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in event.items()}
                self.client.xadd(self.stream_key, payload)
            except Exception:
                pass
