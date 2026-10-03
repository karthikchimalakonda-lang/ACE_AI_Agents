"""Normalize, redact, categorize, and prioritize a new infrastructure incident."""

import io
import json
import re
from datetime import datetime, timezone

from fdk import response


def _redact(value: str) -> str:
    value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[REDACTED_EMAIL]", value)
    value = re.sub(r"(?i)(token|password|secret)\s*[:=]\s*\S+", r"\1=[REDACTED]", value)
    return value


def _severity(metric_value, threshold, summary: str) -> str:
    ratio = float(metric_value or 0) / max(float(threshold or 1), 0.001)
    text = summary.lower()
    if ratio >= 4 or "outage" in text or "unavailable" in text:
        return "critical"
    if ratio >= 2 or "error" in text or "failure" in text:
        return "high"
    return "medium"


def handler(ctx, data: io.BytesIO = None):
    payload = json.loads(data.getvalue().decode("utf-8") or "{}")
    required = ["incident_id", "service", "alert_name", "summary"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        return response.Response(ctx, status_code=400, response_data=json.dumps({"error": "Missing required fields", "fields": missing}))

    summary = _redact(str(payload["summary"]))
    normalized = {
        "incident_id": str(payload["incident_id"]),
        "service": _redact(str(payload["service"])),
        "alert_name": _redact(str(payload["alert_name"])),
        "summary": summary,
        "environment": _redact(str(payload.get("environment", "unknown"))),
        "category": "availability" if any(word in summary.lower() for word in ("error", "latency", "timeout", "unavailable")) else "operational",
        "severity": _severity(payload.get("metric_value"), payload.get("threshold"), summary),
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    return response.Response(ctx, response_data=json.dumps(normalized), headers={"Content-Type": "application/json"})
