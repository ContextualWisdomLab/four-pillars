# ADR 0004: Purpose-bound personal data processing without blanket masking

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Four Pillars needs birth date/time, timezone or location-derived time context, optional personal notes, and generated report content to perform the service the user requested. Replacing those values with blanket masks before calculation or interpretation can make the service unusable or materially change the requested result. At the same time, birth context and report prose can identify a person or reveal sensitive circumstances, and model/provider, telemetry, history, support, and operator paths create disclosure risks.

The architecture therefore needs privacy controls that preserve necessary task data while preventing ambient, secondary, or indefinite use. This decision is a software and governance control; it does not claim CSAP, SOC 2, ISO, or legal certification.

## Decision

Four Pillars SHALL use **purpose-bound processing** rather than blanket masking as its primary privacy design.

1. **Calculation purpose:** validated birth inputs may be processed by the deterministic calculation core because those fields are required to calculate the requested chart and luck periods.
2. **Interpretation purpose:** personal data may cross the selected interpretation boundary only for an approved report-generation purpose, through authenticated/authorized application access, from an explicit field-level input schema, and using the minimum data necessary for that report. Data outside that allow-list is omitted or transformed only by an approved purpose-preserving rule. Provider choice is never inferred from data sensitivity or silently changed.
3. **History/status purpose:** collection/status APIs expose exactly the canonical `ReportJobView` contract documented in `docs/technical/JOB_STATUS_SCHEMA.md`: opaque job ID, lifecycle status, created/updated timestamps, allow-listed completed artifact names, and a nullable sanitized operational error of at most 4,000 characters (expected only for `failed`/`quality_failed`). They do not expose stored birth inputs, notes, report text, request/calculation fingerprints, idempotency material, model traces, credentials, or internal paths.
4. **Attribution/telemetry purpose:** organization attribution and ordinary telemetry must exclude subject labels, birth context, prompts, generated text, calculation fingerprints, artifact paths, credentials, and raw operational PII. Raw PII is never copied into ordinary logs/metrics/traces.
5. **Storage purpose:** durable job storage may retain the validated request for asynchronous processing, but the data is subject to explicit retention/deletion controls and deployment access policy.
6. **Support/privileged access:** operator or break-glass access must be exceptional, authorized, auditable, time-bounded where the platform supports it, and scoped to a support/security purpose. Sensitive raw values are not copied into ordinary logs for convenience.
7. **Secrets:** `NVIDIA_NIM_API_KEY`, `CONTEXTUAL_ORCHESTRATOR_TOKEN`, API authentication material, database credentials, and provider credentials are separate secret classes and may never be placed in prompts, report artifacts, public history, or usage attribution.
8. **Data rights:** production deployments must define deletion/export and retention behavior appropriate to their jurisdiction and role. The standalone product provides terminal-job deletion and bounded default retention; enterprise adapters must preserve or strengthen these semantics.
9. **Encryption and transport:** production public and model-gateway traffic must use authenticated TLS; storage/backups containing personal data require deployment-appropriate encryption and access controls.
10. **Processor/subprocessor transparency:** operators using hosted NIM or an organization gateway must document external recipients, region/data-residency assumptions, provider retention, incident obligations, and contract boundaries before production use.

## Data classification

| Data | Minimum classification | Allowed default use |
|---|---|---|
| Birth date/time/timezone/location-derived context | Confidential personal data | deterministic calculation; approved requested interpretation fields; durable job processing |
| User context/relationship/work notes | Confidential personal data | approved requested interpretation fields only when supplied and necessary |
| Generated report | Confidential user content | rendering, requested retrieval/export, bounded retention |
| Calculation fingerprint | Internal integrity metadata | quality/provenance; not public history/attribution |
| Job UUID/status/timestamps | Operational metadata | authenticated lifecycle/history |
| Sanitized operational error | Operational metadata with residual disclosure risk | canonical status schema, max 4,000 characters, no raw request/prompt/credential/path material |
| Model/prompt version and attempt counts | Operational/provenance metadata | privacy-safe trace/manifest |
| Provider/API/database credentials | Secret | corresponding authenticated transport only |

## Failure and degraded modes

- If a selected model route cannot meet its configured credential or transport boundary, the report job fails visibly; the system does not silently route personal data elsewhere.
- If a history or artifact request is not authorized, it fails closed without revealing sensitive content beyond the minimum API contract.
- If retention cleanup fails, the operator must be able to detect and remediate the failure; a cleanup error is not evidence that deletion occurred.
- If a privacy incident is suspected, preserve the minimum evidence needed for incident response while stopping unnecessary disclosure; do not expand logs by dumping full prompts/reports.

## Consequences

This decision preserves product functionality while materially reducing secondary disclosure. It requires deliberate data-flow documentation, authorization, field-level input contracts, retention, incident handling, and backend/subprocessor governance. It also means “mask all PII” cannot be used as a generic security recommendation when doing so changes the computation or requested interpretation.

## Rejected alternatives

- **Blanket masking before all processing** was rejected because birth/time/context values are functional inputs.
- **Unmask whatever the user mentions** was rejected because a user request does not replace an approved processing purpose, authorization, a field-level input contract, or minimum-necessary disclosure.
- **Store nothing durably** was rejected because asynchronous jobs, recovery, idempotency, and explicit user retrieval require durable state.
- **Put full context in telemetry for debugging** was rejected because ordinary observability is not a valid secondary purpose for sensitive content.
- **Automatic provider fallback** was rejected because it silently changes recipients and privacy/contract boundaries.

## Implementation and test mapping

- `src/four_pillars/jobs.py` — durable request state, lifecycle, retention/deletion support.
- `src/four_pillars/api.py` and `docs/technical/JOB_STATUS_SCHEMA.md` — canonical public status fields and 4,000-character error bound.
- `src/four_pillars/history.py` and API history models — opaque/redacted continuation and collection semantics.
- `src/four_pillars/contextual_orchestrator.py` — prompt-safe organization attribution.
- `src/four_pillars/reporting.py` — UUID artifact layout and approved rendering.
- `SECURITY.md` and `docs/security/THREAT_MODEL.md` — operational controls and threat mapping.
- history/privacy/API tests — ensure public collection/status paths do not expose stored sensitive fields.

## Reversal conditions

Supersede this ADR if the product no longer processes personal birth/context data, if a materially different identity/privacy architecture becomes authoritative, or if a binding deployment requirement necessitates a stricter control that changes product behavior. A new backend alone does not supersede this ADR; it must comply with the same purpose-bound contract.

## References — APA 7th

International Organization for Standardization. (2023). *ISO/IEC 23894:2023 Information technology—Artificial intelligence—Guidance on risk management*. ISO.

International Organization for Standardization. (2023). *ISO/IEC 42001:2023 Information technology—Artificial intelligence—Management system*. ISO.

Autio, C., Schwartz, R., Dunietz, J., Jain, S., Stanley, M., Tabassi, E., Hall, P., & Roberts, K. (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* (NIST AI 600-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.600-1
