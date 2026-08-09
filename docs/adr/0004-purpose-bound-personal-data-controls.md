# ADR 0004: Purpose-bound personal-data controls instead of blanket masking

- Status: Proposed
- Date: 2026-08-09

## Context and drivers

A useful Four Pillars report necessarily processes birth date/time, timezone/location policy, a subject label, optional personal context, generated interpretations, and related artifacts. Blanket PII masking can destroy the data semantics required for deterministic calculation, user-specific reporting, report recovery, deletion/export, and professional-consultant workflows. At the same time, ambient propagation of those values into logs, model attribution, public history, analytics, filenames, or cross-service metadata creates avoidable privacy risk.

The design therefore needs to preserve purpose-required data inside a narrow authorized processing path while minimizing copies and secondary use. ISO/IEC 27701:2025 frames accountable privacy management for PII controllers/processors; ISO/IEC 27001:2022 frames risk-based information-security management; NIST SP 800-207 removes implicit trust based on network location; AICPA Trust Services Criteria cover security, availability, processing integrity, confidentiality, and privacy; and KISA's CSAP program evaluates cloud-service security controls under Korean public-cloud certification rules. These sources guide engineering readiness only and do not imply certification or legal compliance by themselves.

## Decision

Four Pillars shall not use blanket PII masking as the primary privacy control for workflows in which masking would make the product nonfunctional. Instead it shall apply **purpose-bound data handling**:

1. **Purpose classification.** Each processing surface states why a data category is needed: deterministic calculation, report interpretation, artifact rendering, report recovery, support/incident response, or explicit export/deletion.
2. **Minimum payload by boundary.** Send only purpose-required fields to each component. Contextual Orchestrator attribution and public job history contain no birth data, subject label, user notes, report copy, fingerprint, raw traces, internal paths, or provider credentials.
3. **Authorization before access.** Authentication/authorization protects report jobs and artifacts independently of network location. Organization deployments must map tenant/subject/operator authority explicitly.
4. **Identity separation.** Public job identifiers remain opaque random UUIDs. Human identity/account linkage, if introduced, must be held behind a separately authorized mapping rather than embedded in report identifiers or model metadata.
5. **Cryptographic protection.** Production deployments use TLS, encryption at rest for durable PII-bearing storage, separated key management, and bounded credential scopes. Application secrets never enter prompts, report artifacts, or public traces.
6. **Restricted privileged access.** Operational/break-glass access requires a defined purpose, least privilege, auditable actor/time/reason, and post-access review. Routine observability must not require raw birth context.
7. **Retention, deletion and export.** Retention is configurable and bounded; terminal report jobs can be explicitly deleted. Export/deletion actions operate on authoritative job identity and must include associated artifacts. Backups require separately documented retention and restoration deletion semantics before regulated production use.
8. **Audit without content replication.** Security and operations evidence should record actor, action, object identifier, outcome, timestamps, version/digest and authorization decision rather than duplicating report content.
9. **Model and subprocessor boundary.** Deployment owners document model endpoints, subprocessors, region/egress and provider retention where applicable. No selected-backend failure silently changes provider or privacy class.
10. **Fail closed on missing authority.** Missing authentication, unsupported tenant scope, invalid artifact identity, or ambiguous authorization fails rather than widening access.

## Current implementation mapping

Already implemented controls include UUID artifact/job identities, authenticated API support, redacted job-history views, safe browser rendering, prompt-safe orchestrator attribution, explicit retention/deletion operations, non-root container execution, model/provider credential separation, path allow-listing/resolution, and exclusion of raw model content from published trace metadata.

The following remain deployment/product gaps and therefore keep this ADR Proposed: tenant-scoped authorization, production encryption-at-rest/KMS reference profile, audited break-glass workflow, data-residency/subprocessor inventory, backup/restore privacy semantics, formal data-subject export bundle, and tamper-evident privileged-access evidence.

## Alternatives considered

### Mask every personal field before processing

Rejected because deterministic calculation and personalized reporting require the original semantic values. Masking can also create false confidence while leaving linkage, access control, retention, or endpoint risk unresolved.

### Store/process everything and rely on perimeter isolation

Rejected because network placement alone does not define authority and creates unnecessary copies and breach impact.

### Remove durable report jobs entirely

Rejected because professional and platform users require crash recovery, idempotency, recent-work recovery, deletion, and auditable lifecycle state. Durability is retained with bounded scope and retention controls.

## Consequences

- Privacy engineering becomes an authorization/data-flow problem instead of a display-only masking problem.
- Component interfaces must declare which personal fields they consume and why.
- Future multi-tenant adapters require explicit tenant-scoped repositories and object storage rather than shared implicit access.
- Logs and telemetry become less convenient for ad hoc debugging; operational tooling must use identifiers, digests, bounded error metadata, and governed break-glass access when content inspection is actually necessary.

## Failure and recovery

If a component cannot prove authorization or purpose for requested PII, the operation fails closed. If privacy-control configuration is unavailable, the service must not silently emit data into broader telemetry/model metadata. Incident recovery must preserve enough identifier-level evidence to locate affected jobs without copying their full contents into incident tickets or logs.

## Security and governance impact

This decision supports CSAP/SOC 2/ISO privacy-security readiness but is not an attestation or certification claim. Legal basis, consent requirements, international transfer rules, retention obligations, and customer-specific contracts remain deployment/legal responsibilities outside this ADR's software-architecture claim.

## Acceptance evidence

Before this ADR can become Accepted, the repository should include realistic tests and operator evidence for:

- cross-tenant/job authorization denial where tenant mode is introduced;
- public history/telemetry/attribution containing no prohibited personal fields;
- deletion removing current authoritative artifacts and defining backup behavior;
- encryption/key configuration in the supported production profile;
- auditable privileged/break-glass access if raw content inspection exists;
- retention and export workflows that survive restart and partial failure;
- provider/region/retention documentation for hosted interpretation.

## Migration and rollback

Current single-node behavior remains compatible. New tenant/KMS/audit controls should be additive and versioned. Rollback must never re-expose data previously removed from public views or reintroduce plaintext secret/content logging.

## Supersession conditions

Supersede this ADR if the product stops processing personal birth data, adopts a materially different privacy architecture such as client-only calculation/reporting, or an independently reviewed regulatory/contractual requirement forces a different data-control model.

## References

American Institute of Certified Public Accountants. (2023). *2017 Trust Services Criteria for security, availability, processing integrity, confidentiality, and privacy (with revised points of focus—2022)*. https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

International Organization for Standardization, & International Electrotechnical Commission. (2022). *Information security, cybersecurity and privacy protection—Information security management systems—Requirements* (ISO/IEC Standard No. 27001:2022). https://www.iso.org/standard/27001

International Organization for Standardization, & International Electrotechnical Commission. (2025). *Information security, cybersecurity and privacy protection—Privacy information management systems—Requirements and guidance* (ISO/IEC Standard No. 27701:2025). https://www.iso.org/standard/27701

Korea Internet & Security Agency. (2024). *클라우드서비스 보안인증기준 해설서* [Cloud service security certification criteria commentary]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=87&mode=view

Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). *Zero trust architecture* (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207
