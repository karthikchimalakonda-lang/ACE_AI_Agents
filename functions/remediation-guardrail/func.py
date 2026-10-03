"""Apply deterministic safety policy to proposed remediations and require approval for risky actions."""

import io
import json

from fdk import response


RISKY_TERMS = ("restart", "scale", "rollback", "delete", "terminate", "purge", "rotate", "disable")


def handler(ctx, data: io.BytesIO = None):
    payload = json.loads(data.getvalue().decode("utf-8") or "{}")
    actions = payload.get("recommended_actions", [])
    reviewed = []
    for action in actions:
        needs_approval = any(term in action.lower() for term in RISKY_TERMS)
        reviewed.append({"action": action, "status": "requires_human_approval" if needs_approval else "safe_to_investigate", "executed": False})
    result = {
        "incident_id": payload.get("incident_id"),
        "policy": "No remediation action is executed by this workflow.",
        "reviewed_actions": reviewed,
        "approval_required": any(item["status"] == "requires_human_approval" for item in reviewed),
    }
    return response.Response(ctx, response_data=json.dumps(result), headers={"Content-Type": "application/json"})
