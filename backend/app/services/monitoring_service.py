from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock


class MonitoringService:
    """
    Lightweight in-process monitoring for SentinelL402.

    This is the development monitoring layer.

    Later, for multiple FastAPI instances,
    metrics should move to Redis/Prometheus.
    """

    def __init__(
        self,
        max_points: int = 60,
    ) -> None:
        self._lock = Lock()
        self._max_points = max_points

        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0

        self._payment_count = 0
        self._security_analysis_count = 0
        self._agent_request_count = 0
        self._threat_count = 0

        self._request_history: deque[dict] = deque(
            maxlen=max_points
        )

    def record_request(
        self,
        *,
        success: bool = True,
        status_code: int = 200,
        latency_ms: float = 0.0,
    ) -> None:
        with self._lock:
            self._total_requests += 1

            if success:
                self._successful_requests += 1
            else:
                self._failed_requests += 1

            self._request_history.append(
                {
                    "timestamp": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                    "status_code": status_code,
                    "latency_ms": round(
                        latency_ms,
                        2,
                    ),
                }
            )

    def record_payment(self) -> None:
        with self._lock:
            self._payment_count += 1

    def record_security_analysis(
        self,
        *,
        threat_detected: bool = False,
    ) -> None:
        with self._lock:
            self._security_analysis_count += 1

            if threat_detected:
                self._threat_count += 1

    def record_agent_request(self) -> None:
        with self._lock:
            self._agent_request_count += 1

    def snapshot(self) -> dict:
        with self._lock:
            history = list(
                self._request_history
            )

            if history:
                average_latency_ms = (
                    sum(
                        item["latency_ms"]
                        for item in history
                    )
                    / len(history)
                )
            else:
                average_latency_ms = 0.0

            return {
                "timestamp": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
                "requests": {
                    "total": (
                        self._total_requests
                    ),
                    "successful": (
                        self._successful_requests
                    ),
                    "failed": (
                        self._failed_requests
                    ),
                    "average_latency_ms": round(
                        average_latency_ms,
                        2,
                    ),
                },
                "payments": (
                    self._payment_count
                ),
                "security_analyses": (
                    self._security_analysis_count
                ),
                "agent_requests": (
                    self._agent_request_count
                ),
                "threats": (
                    self._threat_count
                ),
                "request_history": history,
            }


monitoring_service = MonitoringService()