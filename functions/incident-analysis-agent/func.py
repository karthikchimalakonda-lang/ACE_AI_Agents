"""Create AI-ready incident hypotheses, evidence checks, and remediation proposals without executing actions."""

import io
import json

from fdk import response


def _analysis(payload: dict) -> dict:
    severity = payload.get("severity", "medium")
    category = payload.get("category", "operational")
    hypotheses = ["Recent application or configuration change", "Upstream dependency degradation"]
    if category == "availability":
        hypotheses.insert(0, "Application capacity saturation or unhealthy deployment")
    recommendations = [
        "Review service error-rate, latency, and dependency metrics for the incident window.",
        "Compare the current deployment and configuration with the last known healthy version.",
    ]
    if severity in {"critical", "high"}:
        recommendations.append("Prepare a controlled rollback or scale-out plan for human approval.")
    return {
        "incident_id": payload.get("incident_id"),
        "analysis_mode": "deterministic-demo; replace with OCI Generative AI in an approved deployment",
        "confidence": 0.72 if severity in {"critical", "high"} else 0.62,
        "probable_causes": hypotheses,
        "evidence_to_collect": ["Service metrics", "Application logs", "Recent deployment history", "Dependency health"],
        "recommended_actions": recommendations,
        "human_review_required": True,
    }


def handler(ctx, data: io.BytesIO = None):
    payload = json.loads(data.getvalue().decode("utf-8") or "{}")
    if not payload.get("incident_id"):
        return response.Response(ctx, status_code=400, response_data=json.dumps({"error": "incident_id is required"}))
    return response.Response(ctx, response_data=json.dumps(_analysis(payload)), headers={"Content-Type": "application/json"})
