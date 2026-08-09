# Four Pillars Personal-Data Governance

- Status: Engineering baseline; not a legal opinion, certification, or customer-specific data-processing agreement
- Reviewed: 2026-08-09

## Principle

Four Pillars cannot provide deterministic birth-chart calculation or personalized report generation if every personal value is indiscriminately masked before use. The privacy objective is therefore **not blanket masking**. It is to keep purpose-required data usable inside a narrow authorized processing path while preventing unnecessary persistence, copying, linkage, telemetry, attribution, model metadata, and cross-service exposure.

This document applies the direction proposed in ADR 0004. Until the remaining deployment controls are implemented and reviewed, it is an engineering target as well as a description of existing safeguards.

## Data classes and purpose

| Data class | Examples | Necessary purposes | Default prohibited secondary propagation |
|---|---|---|---|
| `birth_input` | birth date/time, calendar type, timezone, solar-time policy | deterministic calculation; boundary warnings | public history, telemetry dimensions, filenames, model usage attribution |
| `subject_context` | subject label, optional user notes | report wording and requested context | public history, usage attribution, generic logs, unrelated analytics |
| `calculation_evidence` | pillars, solar-term boundaries, Ten Gods, fingerprint | report grounding, verification, reproducibility | identity tracking, marketing profile |
| `fortune_evidence` | daewoon/annual/monthly snapshots | requested interpretation | unrelated profiling/analytics |
| `report_content` | generated JSON/HTML/PDF | delivery, recovery, user export | public history, ambient logs, model attribution |
| `job_metadata` | UUID, state, timestamps, bounded error | queue, history, support | reconstruction of birth/context without authorized job read |
| `model_trace_metadata` | model identifier, attempt/repair counts, prompt versions | reproducibility, provider operations | raw generated content, credentials, unnecessary PII |
| `provider_credentials` | NIM/orchestrator/API keys | authenticated service calls | DB rows, prompts, reports, traces, analytics |
| `identity_linkage` | future tenant/account-to-job mapping | authorization and data rights | public IDs, provider metadata, report filenames |

## Data-flow rules

### Deterministic calculation

The calculator may receive the complete validated birth input required by the configured calendar/time policy. It must not need a model credential, external network, report repository, or identity provider. Calculation output carries an evidence version and fingerprint so downstream components need not reinterpret the original calendar facts.

### Interpretation

The selected interpreter receives only the calculation/luck evidence plus user context needed for the requested report. Direct NIM uses `NVIDIA_NIM_API_KEY`; Contextual Orchestrator uses its separate token. Provider credentials never become prompt values. Organizational attribution contains service/organization labels only and excludes birth input, notes, report copy, fingerprints, file paths and credentials.

### Persistence and history

The standalone `report_jobs` table stores a validated request because durable asynchronous generation and recovery require it. The public collection API returns a redacted job view and does not serialize the stored request. History cursors contain only a versioned UTC timestamp and random job UUID boundary.

### Artifacts

Artifacts are stored beneath random job identifiers, not personal filenames. Allow-listed artifact names prevent arbitrary path access. HTML rendering escapes user-controlled content. Production object storage must provide equivalent authorization and path/object-key isolation.

### Observability

Routine logs/metrics should use job ID, state, duration, provider/model identifier, bounded error class, version and digest fields. Raw birth/context/report content is not a routine observability field. If deep incident diagnosis requires content, use a separate privileged support path with reason, actor, object, time, bounded access and post-access review.

## Authorization model

Current standalone deployments may use the repository's API-key digest authentication. That is not a complete multi-tenant identity model. Organization/multi-tenant deployments must add explicit tenant/subject authorization without changing public job IDs into identity-bearing identifiers.

Target policy:

- authenticate user/service/device according to deployment policy;
- authorize the specific action on the specific job/artifact/tenant;
- never infer authorization from possession of a UUID or network location;
- deny cross-tenant enumeration and artifact access;
- separate ordinary user, support/operator and break-glass roles;
- record privileged authorization decisions without copying protected content into the audit event.

## Cryptographic and secret controls

- TLS for non-loopback production traffic.
- Encryption at rest for PII-bearing database and artifact storage in production profiles.
- Keys managed separately from data; production should use KMS/HSM or an equivalent organization-controlled key service.
- Separate API authentication, direct NIM, Contextual Orchestrator and GitHub automation credentials.
- Least-privilege scopes and short-lived tokens where supported.
- No secrets in prompts, artifacts, public traces, source-controlled `.env`, issue bodies or PR metadata.

## Retention, deletion, export and backup

Current default report retention is bounded and terminal jobs can be deleted. Regulated production profiles must additionally define:

- retention by purpose/data class;
- immediate deletion workflow for active authoritative records/artifacts;
- export format and authorization;
- backup retention and delayed deletion behavior;
- restoration controls that do not resurrect records past their retention/legal state without an explicit governed recovery decision;
- evidence that deletion/export jobs survive retries and partial failure.

## Break-glass support instead of ambient masking

When production support genuinely needs protected values, the safer alternative to either blanket masking or universal engineer access is controlled break-glass access:

1. authenticate an eligible privileged operator;
2. require a ticket/reason/purpose and bounded time window;
3. authorize only the affected tenant/job/data classes;
4. expose the minimum necessary content through a dedicated surface;
5. log actor, purpose, scope, start/end and outcome without duplicating the content itself;
6. review the access after the incident;
7. revoke temporary elevation automatically.

This capability is a target-state requirement; it must not be claimed as implemented until code/deployment evidence exists.

## Processor, region and egress boundary

Before regulated/enterprise operation, deployment owners must maintain an inventory of:

- selected interpretation backend and model endpoint;
- data categories sent to that backend;
- hosting/processing region when contractually relevant;
- subprocessors and retention/training terms where applicable;
- egress policy and DNS/TLS controls;
- organization gateway responsibilities versus Four Pillars responsibilities;
- incident-notification and deletion obligations.

A backend outage never justifies a silent switch to another provider or privacy class.

## CSAP and SOC 2 readiness relationship

The controls above are intended to make evidence collection compatible with later CSAP and SOC 2 readiness work, but only an applicable CSAP certification process or independent SOC 2 examination can establish those external outcomes. Repository tests and diagrams are engineering evidence, not certification.

## Required tests and operational evidence

- negative tests proving public history/trace/attribution schemas exclude protected fields;
- authorization tests for job/artifact access and future cross-tenant isolation;
- retention/deletion integration tests including failure/retry behavior;
- secret-scan and log tests preventing raw credential/content leakage;
- object/path traversal and symlink defenses;
- provider request fixtures proving only intended payload/metadata leaves the service;
- backup/restore and break-glass acceptance tests before those profiles are advertised;
- audit evidence that privileged access cannot be performed through ordinary public history APIs.

## References

American Institute of Certified Public Accountants. (2023). *2017 Trust Services Criteria for security, availability, processing integrity, confidentiality, and privacy (with revised points of focus—2022)*. https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

International Organization for Standardization, & International Electrotechnical Commission. (2022). *Information security, cybersecurity and privacy protection—Information security management systems—Requirements* (ISO/IEC Standard No. 27001:2022). https://www.iso.org/standard/27001

International Organization for Standardization, & International Electrotechnical Commission. (2025). *Information security, cybersecurity and privacy protection—Privacy information management systems—Requirements and guidance* (ISO/IEC Standard No. 27701:2025). https://www.iso.org/standard/27701

Korea Internet & Security Agency. (2024). *클라우드서비스 보안인증기준 해설서* [Cloud service security certification criteria commentary]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=87&mode=view

Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). *Zero trust architecture* (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207
