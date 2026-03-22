from __future__ import annotations

from collections import defaultdict
from threading import Lock


class InMemoryMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._request_count = 0
        self._status_counts: dict[int, int] = defaultdict(int)
        self._total_duration_ms = 0.0

    def record(self, status_code: int, duration_ms: float) -> None:
        with self._lock:
            self._request_count += 1
            self._status_counts[status_code] += 1
            self._total_duration_ms += duration_ms

    def snapshot(self) -> dict:
        with self._lock:
            avg = self._total_duration_ms / self._request_count if self._request_count else 0.0
            return {
                "request_count": self._request_count,
                "status_counts": dict(self._status_counts),
                "avg_duration_ms": round(avg, 2),
            }


metrics_store = InMemoryMetrics()
