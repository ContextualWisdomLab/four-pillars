# Four Pillars CSAP and SOC 2 Readiness Map

- Status: Engineering readiness map only
- Reviewed: 2026-08-09
- Certification/attestation status: **none claimed**

## Claim boundary

Four Pillars is not currently represented as CSAP-certified, SOC 2-attested, ISO/IEC 27001-certified, or ISO/IEC 27701-certified. This document maps product engineering controls and evidence gaps so a future deployment can prepare for an applicable assessment. Certification and attestation require external scope, organizational controls, operating evidence, and assessor/auditor procedures that source code alone cannot satisfy.

KISA describes CSAP as a security-certification program for cloud computing services under Korean law, with defined certification/evaluation bodies, certification scope, service types, grades and periodic assessments. AICPA's Trust Services Criteria provide criteria relevant to Security, Availability, Processing Integrity, Confidentiality and Privacy for SOC examinations. These are different assurance regimes and must not be conflated.

## Scope assumptions

This map treats the repository as one product component. A real assessment scope must additionally identify:

- organization/legal entity and responsible control owners;
- cloud accounts, regions, networks, CI/CD, secret stores and identity systems;
- managed databases/object storage/KMS and backup locations;
- NVIDIA NIM or organization-model subprocessors and contractual terms;
- central `.github`, `contextual-orchestrator`, observability, incident and support dependencies;
- production change-management/release process;
- customer/tenant support and privileged-access process;
- policies, training, vendor management and operating evidence outside the repository.

## Readiness matrix

| Control family | Existing repository evidence | Material gaps before assessment readiness |
|---|---|---|
| Security governance | `SECURITY.md`, ADRs, standards traceability, protected PR checks, SAST/security scans | named organizational control owners, policy approval cadence, risk register, exceptions process, operating evidence |
| Change management | reviewed PRs, exact-head CI, release workflow, CHANGELOG, immutable action pins | organization-wide change tickets/approvals as required, emergency-change procedure, production-deployment evidence |
| Software supply chain | hash-locked CI dependencies, container build, action SHA pins, release checksums | complete SBOM/provenance publication/verification for every release and deployment, artifact signing policy if required |
| Logical access | optional API-key digest auth, provider credential separation, GitHub App least-privilege design | production SSO/tenant RBAC/ABAC, joiner-mover-leaver controls, periodic access reviews, service-account inventory |
| Privileged access | development/review/merge authority separation | implemented break-glass workflow, time-bounded elevation, post-access review, production privileged-session evidence |
| Network/egress | TLS requirement for remote credential-bearing endpoints; explicit provider URL policy | production network segmentation/egress enforcement evidence, DNS/TLS policy, firewall/WAF/load-balancer architecture by deployment |
| Data confidentiality | redacted public history, opaque IDs, no secrets in model attribution, artifact path allow-listing | production encryption-at-rest/KMS profile, field/object/tenant access model, key lifecycle/rotation evidence |
| Privacy | purpose-bound data-governance model, retention/deletion API, restricted public history | legal basis/notice/contract mapping, data-subject export package, tenant/account linkage controls, backup deletion semantics, processor/region inventory |
| Availability | health/readiness, durable SQLite queue, worker/API separation, bounded retries | production SLOs, capacity/error budgets, HA target, backup restore exercises, disaster recovery RTO/RPO evidence |
| Processing integrity | deterministic calculation fingerprints, KASI/NAOJ fixtures, Pydantic schemas, quality gates, idempotency | protected-main end-to-end release acceptance dataset, production reconciliation/monitoring, multi-node adapter correctness evidence |
| Logging/monitoring | bounded job state/errors, privacy-safe trace metadata | centralized tamper-resistant audit trail, security alert ownership/escalation, log retention and clock/source integrity evidence |
| Incident management | security reporting and runbooks | organization incident response plan, roles/on-call, notification criteria, tabletop/live exercises, evidence retention |
| Vulnerability management | SAST/Security Scan/dependency review patterns | formal remediation SLA by severity, asset inventory correlation, production scanning/patch evidence |
| Backup/recovery | durable job/artifact concepts and cleanup | encrypted backups, restore testing, backup access separation, retention/deletion propagation |
| Tenant isolation | modular repository/publisher ports | implemented tenant identity/scoping, cross-tenant negative tests, tenant-specific export/delete/audit controls |
| Vendor/subprocessor | explicit NIM/orchestrator boundary and no silent fallback | approved vendor inventory, DPA/retention/training/region terms, continuous vendor review, incident obligations |

## CSAP-specific engineering considerations

The CSAP applicability and target level depend on the actual cloud-service type, public-sector use case, deployment and current Korean certification rules. Engineering work should therefore preserve evidence needed to define an eventual certification scope rather than claiming one prematurely.

Repository/deployment targets include:

- inventory all service assets, supporting services and organizations in scope;
- make cloud/region/network/identity/secret/log/backup boundaries explicit;
- least-privilege administrative and service identities;
- encryption/key-management and access-control evidence for PII-bearing stores;
- tenant isolation and secure deletion/export;
- vulnerability/security test evidence tied to released artifacts;
- incident, backup/restore, change and release operating procedures;
- supply-chain/component/SBOM evidence;
- explicit third-party model/provider and organization gateway boundaries.

KISA's current public materials must be rechecked before an actual certification project because certification types, grades, guidance and assessment procedures can change independently of this repository.

## SOC 2-specific engineering considerations

AICPA's Trust Services Criteria are relevant to an examination of controls, not a source-code compliance badge. Four Pillars should be capable of producing operating evidence for whichever categories are included in a future system description:

- **Security:** access, change, vulnerability, incident, secret, network and supply-chain controls;
- **Availability:** monitoring, capacity, backup/restore, resilience, incident recovery and SLO evidence;
- **Processing Integrity:** deterministic calculation fidelity, job idempotency/state integrity, schema validation, artifact hashing and release acceptance;
- **Confidentiality:** encryption, authorization, restricted content propagation, provider boundaries and retention;
- **Privacy:** purpose, notice/contract obligations, collection/use/retention/disclosure/deletion/export controls and accountable PII processing.

A real SOC 2 examination depends on control design **and operation over the examination period**. Passing CI does not establish that operating-effectiveness evidence.

## Evidence backlog

High-priority evidence/product gaps for enterprise/public-sector readiness:

1. production reference deployment with tenant-scoped identity and authorization;
2. encryption-at-rest/KMS reference architecture and automated configuration checks;
3. tamper-resistant security/privileged audit events without duplicating report PII;
4. explicit break-glass workflow;
5. durable export/deletion workflow including artifact and backup semantics;
6. backup/restore runbook plus regular recovery exercise evidence;
7. SBOM/provenance publication and verification integrated with SemVer release artifacts;
8. vendor/subprocessor/region inventory for direct NIM and orchestrated modes;
9. production SLO/SLI and incident escalation criteria;
10. tenant-isolation and cross-tenant negative integration tests for remote adapters;
11. control-evidence retention and assessor-readable export;
12. documented responsibility matrix between Four Pillars, central `.github`, Contextual Orchestrator and hosting platform.

## No-blanket-masking position

Neither CSAP readiness nor SOC 2 readiness justifies masking data required to perform an authorized business function. Four Pillars instead minimizes **where** personal content appears and **who/what may access it**, using purpose-bound authorization, restricted linkage, encryption, retention, deletion/export, provider boundaries and auditable privileged access. Public/telemetry surfaces should remain content-minimized even though the authorized deterministic/reporting path handles the semantic birth/context data.

## Release gate implications

A release may advertise a readiness control only when the exact integrated protected head and deployment evidence support it. Release notes must distinguish:

- repository control implemented and tested;
- reference-deployment control available but operator-configured;
- planned control not yet implemented;
- external certification/attestation not obtained.

## References

American Institute of Certified Public Accountants. (2022). *SOC 2® reporting on an examination of controls at a service organization relevant to security, availability, processing integrity, confidentiality, or privacy*. AICPA & CIMA.

American Institute of Certified Public Accountants. (2023). *2017 Trust Services Criteria for security, availability, processing integrity, confidentiality, and privacy (with revised points of focus—2022)*. https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

International Organization for Standardization, & International Electrotechnical Commission. (2022). *Information security, cybersecurity and privacy protection—Information security management systems—Requirements* (ISO/IEC Standard No. 27001:2022). https://www.iso.org/standard/27001

International Organization for Standardization, & International Electrotechnical Commission. (2025). *Information security, cybersecurity and privacy protection—Privacy information management systems—Requirements and guidance* (ISO/IEC Standard No. 27701:2025). https://www.iso.org/standard/27701

Korea Internet & Security Agency. (2024). *클라우드 서비스 보안인증제 안내서* [Cloud service security certification program guide]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=86&mode=view

Korea Internet & Security Agency. (2024). *클라우드서비스 보안인증기준 해설서* [Cloud service security certification criteria commentary]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=87&mode=view
