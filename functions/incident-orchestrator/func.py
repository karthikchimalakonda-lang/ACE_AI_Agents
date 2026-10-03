"""Combine normalized incident, analysis, and guardrail results into a review-ready response."""

import io
import json
from datetime import datetime, timezone

from fdk import response


def handler(ctx, data: io.BytesIO = None):
    payload = json.loads(data.getvalue().decode("utf-8") or "{}")
    incident = payload.get("incident", {})
    analysis = payload.get("analysis", {})
    guardrail = payload.get("guardrail", {})
    if not incident.get("incident_id"):
        return response.Response(ctx, status_code=400, response_data=json.dumps({"error": "incident.incident_id is required"}))
    result = {
        "incident_id": incident["incident_id"],
        "status": "awaiting_human_review" if guardrail.get("approval_required", True) else "ready_for_investigation",
        "severity": incident.get("severity"),
        "service": incident.get("service"),
        "summary": incident.get("summary"),
        "analysis": analysis,
        "guardrail": guardrail,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "automation_boundary": "This workflow proposes and validates actions; it does not execute infrastructure changes.",
    }
    return response.Response(ctx, response_data=json.dumps(result), headers={"Content-Type": "application/json"})
