from collections import deque
from copy import deepcopy
from datetime import datetime, timezone


metrics_data = {
    "total_requests": 0,
    "total_errors": 0,
    "total_response_time_ms": 0.0,
    "average_response_time_ms": 0.0,
    "endpoints": {},
    "status_codes": {},
    "cache": {
        "hits": 0,
        "misses": 0,
    },
}

recent_errors = deque(maxlen=10)


def record_request(method: str, path: str, status_code: int, response_time_ms: float):
    metrics_data["total_requests"] += 1
    metrics_data["total_response_time_ms"] += response_time_ms
    metrics_data["average_response_time_ms"] = round(
        metrics_data["total_response_time_ms"] / metrics_data["total_requests"],
        2,
    )

    endpoint_metrics = metrics_data["endpoints"].setdefault(
        path,
        {
            "count": 0,
            "total_response_time_ms": 0.0,
            "average_response_time_ms": 0.0,
        },
    )
    endpoint_metrics["count"] += 1
    endpoint_metrics["total_response_time_ms"] += response_time_ms
    endpoint_metrics["average_response_time_ms"] = round(
        endpoint_metrics["total_response_time_ms"] / endpoint_metrics["count"],
        2,
    )

    status_key = str(status_code)
    metrics_data["status_codes"][status_key] = metrics_data["status_codes"].get(status_key, 0) + 1

    if status_code >= 400:
        metrics_data["total_errors"] += 1
        recent_errors.appendleft(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": method,
                "path": path,
                "status_code": status_code,
                "response_time_ms": round(response_time_ms, 2),
            }
        )


def record_cache_hit():
    metrics_data["cache"]["hits"] += 1


def record_cache_miss():
    metrics_data["cache"]["misses"] += 1


def get_metrics():
    snapshot = deepcopy(metrics_data)
    snapshot["recent_errors"] = list(recent_errors)
    return snapshot
