# Architecture and safety model

## Data contract

Each stage accepts structured JSON and produces structured JSON. The orchestrator can invoke stages synchronously for a short-running workflow or through an event-driven queue for production workloads.

## AI role

The analysis stage is AI-ready: a deployment can call OCI Generative AI with a restricted, sanitized prompt. Its output is treated as a recommendation, never as an autonomous remediation command.

## Guardrails

- Secrets and sensitive identifiers are redacted before analysis.
- Low-confidence analysis requires human review.
- Restart, scale, delete, terminate, purge, and credential-rotation actions require human approval.
- The project never executes a remediation action; it only returns proposals.
