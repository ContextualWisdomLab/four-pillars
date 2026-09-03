# Doctoring: Canonical Architecture Documentation and Governance

**Date reviewed:** 2026-08-09  
**Purpose:** Record the primary standards and authoritative guidance used to make the Four Pillars documentation graph, privacy architecture, secure-development controls, and AI-governance evidence auditable.  
**Claim boundary:** These sources guide engineering decisions. They do not make Four Pillars ISO-certified, NIST-certified, CSAP-certified, SOC 2-attested, or scientifically validate traditional Four Pillars interpretation.

## 1. Architecture description

### Source

International Organization for Standardization. (2022). *ISO/IEC/IEEE 42010:2022 Software, systems and enterprise—Architecture description* (2nd ed.). ISO.

### Current-source evidence

ISO lists ISO/IEC/IEEE 42010:2022 as the current second edition, published in November 2022, replacing the withdrawn 2011 edition. The standard specifies requirements for architecture descriptions, including concepts, relationships, viewpoints, model kinds, architecture description frameworks, and architecture description languages.

### Product mapping

- `docs/standards/DOCUMENTATION_AUDIT.md` defines stakeholder concerns and canonical viewpoints.
- `docs/architecture/SYSTEM_ARCHITECTURE.md` separates product, deterministic calculation, AI interpretation, persistence, security/privacy, deployment, automation/governance, and release viewpoints.
- ADR 0005 distinguishes architecture from mutable descriptions such as PR bodies and generated plans.
- UML, ERD/data model, threat model, test strategy, and operability remain separate model kinds rather than being flattened into one root diagram.

### Residual gap

This is an engineering alignment, not a formal 42010 conformance assessment. A future acquisition package may add an explicit concern→viewpoint→model inventory if a buyer requires formal architecture-description conformance evidence.

## 2. Product quality

### Source

International Organization for Standardization. (2023). *ISO/IEC 25010:2023 Systems and software engineering—Systems and software Quality Requirements and Evaluation (SQuaRE)—Product quality model* (2nd ed.). ISO.

### Current-source evidence

ISO lists the 2023 second edition as the current product quality model. It defines nine quality characteristics and explicitly supports requirements specification, design objectives, testing objectives, quality criteria, acceptance criteria, and product-quality measurement.

### Product mapping

- PRD success/NFRs and `TEST_STRATEGY.md` bind quality claims to measurable evidence.
- `OPERABILITY.md` separates availability/recovery/operator concerns from hosted-model behavior.
- Documentation completeness is treated as maintainability/acquisition evidence rather than a word-count target.
- 100% owned production statement/branch coverage is a repository-specific gate, not an ISO requirement.

## 3. AI management and risk

### Sources

International Organization for Standardization. (2023). *ISO/IEC 42001:2023 Information technology—Artificial intelligence—Management system*. ISO.

International Organization for Standardization. (2023). *ISO/IEC 23894:2023 Information technology—Artificial intelligence—Guidance on risk management*. ISO.

Tabassi, E. (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)* (NIST AI 100-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.100-1

Autio, C., Schwartz, R., Dunietz, J., Jain, S., Stanley, M., Tabassi, E., Hall, P., & Roberts, K. (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile* (NIST AI 600-1). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.AI.600-1

### Current-source evidence

ISO lists ISO/IEC 42001:2023 and ISO/IEC 23894:2023 as published current standards. NIST AI RMF 1.0 remains published but NIST states it is being revised; NIST AI 600-1 remains the published Generative AI profile and was updated on the NIST site in April 2026.

### Product mapping

- deterministic evidence is outside LLM authority;
- provider selection is explicit and no silent fallback changes recipients;
- model output is schema/quality validated;
- model traces/prompt versions support evaluation;
- hosted tests are bounded and separated from deterministic CI;
- `THREAT_MODEL.md` treats prompt injection, provider pivot, false authority, privacy, and model-development credentials as explicit threats;
- `AUTONOMOUS_DEVELOPMENT.md` requires comparable-budget reasoning/orchestration evidence for material routing/conduct changes.

### Residual gap

The repository does not claim an AIMS or formal AI RMF assessment. NIST AI RMF is under revision in 2026, so future updates must re-evaluate mappings rather than hard-code the 2023 framework as permanently current.

## 4. Secure software development

### Final normative source used by this baseline

Scarfone, K., Souppaya, M., & Dodson, D. (2022). *Secure Software Development Framework (SSDF) Version 1.1: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218

### Newer draft tracked but not treated as final

Booth, H., Ogata, M., Kent, K., Souppaya, M., & Dodson, D. (2025). *Secure Software Development Framework (SSDF) Version 1.2: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218 Rev. 1, Initial Public Draft). National Institute of Standards and Technology.

### Current-source evidence

NIST's SSDF publication page identifies SP 800-218 Version 1.1 as final and SP 800-218 Rev. 1 / Version 1.2 as a December 2025 initial public draft whose public-comment period has closed. This baseline therefore uses final v1.1 for normative engineering traceability while tracking the draft for future changes.

### Product mapping

- exact-head CI and review evidence;
- dependency/SAST/container/package gates;
- immutable/checksum-pinned actions and OpenCode artifact handoff where applicable;
- no model merge/release/reviewer authority;
- threat model, incident, backup/restore and vulnerability reporting;
- test-first root-cause repair and recurrence prevention.

## 5. Purpose-bound personal data

The standards above do not instruct Four Pillars to retain all PII or to blanket-mask it. ADR 0004 applies a product-specific architecture principle: data required for deterministic calculation or a user-requested interpretation remains available inside the relevant trust boundary, while secondary disclosure is limited through purpose limitation, authorization, minimum necessary transport, restricted telemetry/attribution, retention/deletion, encryption/access control, and auditable privileged access.

This design must be re-evaluated against applicable law, contracts, CSAP requirements, and SOC 2 control design for each real production deployment. Repository architecture cannot certify an operator's legal basis or organizational controls.

## 6. Review cadence

Re-check these sources when:

- ISO publishes a new edition or amendment affecting a cited architecture/quality/AI control;
- NIST finalizes SSDF 1.2 or a revised AI RMF;
- Four Pillars adds a new provider/recipient, durable data class, identity/tenant model, distributed architecture, autonomous-development authority, or high-stakes user claim;
- a procurement/certification target requires a control-specific crosswalk.
