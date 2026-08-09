# Documentation, Architecture, Privacy, and Assurance Doctoring

- Review date: 2026-08-09
- Repository baseline reviewed: `ContextualWisdomLab/four-pillars@cd4f4e6361238a1db43c28540640a407c7bf7c6e`
- Purpose: record the external evidence and claim boundaries used by the 2026-08-09 documentation baseline

## Claim boundary

This doctoring record justifies **how the repository documents and governs its architecture, requirements, personal-data handling, security, and assurance readiness**. It does not establish scientific predictive validity for traditional Four Pillars interpretation, does not certify the product against ISO standards, and does not constitute a CSAP certificate or SOC 2 report.

The audit found a code-current documentation defect: prior TRD/traceability prose described the Contextual Orchestrator path as provider-native JSON `response_format` while protected-main `ContextualOrchestratorClient` explicitly configures `native_json_mode=False`. The documentation baseline corrects the prose to the code-current contract: the application prompt requests JSON, Four Pillars parses/validates with Pydantic, and bounded same-backend repair remains available without provider-native JSON mode.

## Architecture-description evidence

### ISO/IEC/IEEE 42010:2022

The ISO catalog lists ISO/IEC/IEEE 42010:2022, *Software, systems and enterprise—Architecture description*, as the published architecture-description standard. The baseline therefore uses explicit concerns/viewpoints rather than one monolithic architecture page: product PRD, technical TRD, root architecture, ADRs, runtime/control-plane UML, conceptual/logical ERD, privacy/security views, operations, and standards traceability.

**Implementation mapping.** `docs/architecture/DOCUMENTATION_MAP.md` defines those viewpoints and their update triggers; `docs/uml/architecture.md`, `docs/uml/control-plane.md`, and `docs/erd/domain-model.md` keep runtime, repository authority, and information-model concerns separately reviewable.

**Limitation.** The repository has not been independently assessed for formal conformance to ISO/IEC/IEEE 42010.

### ISO/IEC/IEEE 29148:2018 and Edition 3 draft

The ISO catalog identifies ISO/IEC/IEEE 29148:2018 as the current published requirements-engineering edition and records that it was confirmed in 2024. ISO also exposes an Edition 3 project at DIS stage during this review.

**Decision.** Four Pillars continues to cite the published 2018 edition for current requirements-engineering guidance and monitors the Edition 3 draft. A DIS is not treated as a final normative replacement before publication and review.

**Implementation mapping.** PRD and TRD distinguish stakeholder/product requirements from technical requirements, acceptance evidence, exclusions, non-functional requirements, provider/data boundaries, and release scope.

## UML notation evidence

OMG UML 2.5.1 is the current formal UML specification referenced by this baseline for class, component, sequence, state, and deployment concepts. Four Pillars stores diagram source as Mermaid/PlantUML for reviewability.

**Claim boundary.** Mermaid is a practical source notation; Four Pillars does not claim XMI interchange compliance or OMG tool certification.

## Security and privacy evidence

### ISO/IEC 27001:2022

ISO/IEC 27001:2022 supplies risk-based information-security management requirements. The baseline applies it as governance context for access, change, incident, supplier, asset, cryptographic, and continual-improvement evidence.

**Claim boundary.** Source code and repository workflow controls do not establish an ISO/IEC 27001 certificate or full organizational ISMS.

### ISO/IEC 27701:2025

ISO/IEC 27701:2025 is the current privacy-information-management edition; ISO lists the older 2019 edition as withdrawn. The 2025 edition expands the privacy-management-system framing for PII controllers/processors.

**Decision.** Four Pillars does not rely on blanket PII masking when it would destroy authorized calculation/reporting functionality. The software instead targets purpose limitation, boundary-specific minimum payloads, explicit authorization, restricted identity linkage, encryption/key separation, retention/deletion/export, processor/region inventory, and governed privileged access.

**Implementation mapping.** `docs/security/DATA_GOVERNANCE.md`, ADR 0004, the redacted history API, privacy-safe usage attribution, opaque UUID artifact/job paths, deletion/retention, and provider credential separation implement or specify those boundaries.

**Residual gaps.** Production tenant authorization, KMS reference configuration, break-glass workflow, backup deletion semantics, subject export, and tamper-resistant privileged audit evidence remain incomplete and are therefore not described as current controls.

### NIST SP 800-207

NIST SP 800-207 defines zero trust as removing implicit trust based on network location and focusing authentication/authorization around resources, users, and services.

**Application.** Job UUIDs, history cursors, network placement, and possession of an artifact path are not treated as authorization. Multi-tenant deployments must add explicit tenant/subject authorization and service identity.

## CSAP evidence boundary

KISA publishes the Cloud Service Security Certification program introduction, 2024 program guide, and 2024 unified criteria commentary. The documents define a Korean public cloud-service certification program with assessment scope and current certification requirements/processes.

**Decision.** Four Pillars maintains a source/deployment readiness map but does not claim CSAP certification. An actual project must revalidate current KISA guidance, cloud-service type/grade/scope, hosting architecture, organizational control ownership, operating evidence, and assessor requirements.

**Implementation mapping.** `docs/compliance/CSAP_SOC2_READINESS.md` inventories repository evidence and gaps for logical access, change management, vulnerability management, cryptography, tenant isolation, logging, incident response, backup/recovery, vendor/processors, and release provenance.

## SOC 2 evidence boundary

AICPA's Trust Services Criteria provide criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy, and AICPA's SOC 2 guide describes examinations of controls at service organizations.

**Decision.** Four Pillars uses those categories to organize engineering readiness evidence but does not represent CI, code review, or the readiness matrix as a SOC 2 report. Operating effectiveness over an examination period and an independent practitioner are external requirements.

**Implementation mapping.** The readiness map explicitly separates repository controls from deployment controls and organizational evidence such as access review, incident response, backup exercises, vendor management, and privileged-access operation.

## Repository-control-plane evidence

The current protected-main automation contains two implemented roles: a model-free minute-17 deterministic quality sentinel and a minute-47 NVIDIA/OpenCode product-development workflow. The active minute-07 exact-head PR steward remains Proposed until its PR merges.

**Decision drivers.** Model proposal/repair, deterministic verification, independent review, merge authority, and release authority remain separate. Model-backed development uses `NVIDIA_NIM_API_KEY`, never `COPILOT_GITHUB_TOKEN`, and does not reuse reviewer-agent credentials.

**Implementation mapping.** ADR 0007 and `docs/uml/control-plane.md` define authority zones and exact-state binding. The documentation baseline intentionally delays conflicting edits to root `ARCHITECTURE.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `CHANGELOG.md`, and `scripts/check_docs.py` until the active PR owning those files resolves.

## Release-provenance evidence

Protected-main `.github/workflows/release.yml` validates source, builds source/wheel and the pinned runtime image, publishes `SHA256SUMS`, targets `GITHUB_SHA`, and refuses to overwrite an existing version release.

**Residual gap.** A mandatory release SBOM, standardized provenance/attestation, and artifact-signature verification are not yet part of the release contract. ADR 0009 therefore remains Proposed.

## Source-retrieval notes

- ISO/IEC/IEEE 42010 catalog consulted 2026-08-09.
- ISO/IEC/IEEE 29148:2018 catalog and Edition 3 DIS project page consulted 2026-08-09.
- OMG UML 2.5.1 specification page consulted 2026-08-09.
- ISO/IEC 27001:2022 and ISO/IEC 27701:2025 catalog pages consulted 2026-08-09.
- NIST SP 800-207 publication consulted 2026-08-09.
- KISA CSAP introduction and 2024 guide/commentary consulted 2026-08-09.
- AICPA Trust Services Criteria and SOC 2 guidance consulted 2026-08-09.

These sources are version-sensitive. Changes in a standards catalog, KISA certification program, AICPA criteria/guidance, or NIST publication create a review obligation; they do not silently mutate product behavior.

## APA 7th references

American Institute of Certified Public Accountants. (2022). *SOC 2® reporting on an examination of controls at a service organization relevant to security, availability, processing integrity, confidentiality, or privacy*. AICPA & CIMA.

American Institute of Certified Public Accountants. (2023). *2017 Trust Services Criteria for security, availability, processing integrity, confidentiality, and privacy (with revised points of focus—2022)*. AICPA & CIMA. https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

International Organization for Standardization, & International Electrotechnical Commission. (2022). *Information security, cybersecurity and privacy protection—Information security management systems—Requirements* (ISO/IEC Standard No. 27001:2022). https://www.iso.org/standard/27001

International Organization for Standardization, & International Electrotechnical Commission. (2025). *Information security, cybersecurity and privacy protection—Privacy information management systems—Requirements and guidance* (ISO/IEC Standard No. 27701:2025). https://www.iso.org/standard/27701

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2018). *Systems and software engineering—Life cycle processes—Requirements engineering* (ISO/IEC/IEEE Standard No. 29148:2018). https://www.iso.org/standard/72089.html

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2022). *Software, systems and enterprise—Architecture description* (ISO/IEC/IEEE Standard No. 42010:2022). https://www.iso.org/standard/74393.html

Korea Internet & Security Agency. (2024). *클라우드 서비스 보안인증제 안내서* [Cloud Service Security Certification program guide]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=86&mode=view

Korea Internet & Security Agency. (2024). *클라우드서비스 보안인증기준 해설서* [Cloud service security certification criteria commentary]. https://isms.kisa.or.kr/main/csap/notice/?boardId=bbs_0000000000000004&cntId=87&mode=view

Object Management Group. (2017). *OMG Unified Modeling Language (OMG UML), version 2.5.1*. https://www.omg.org/spec/UML/2.5.1

Rose, S., Borchert, O., Mitchell, S., & Connelly, S. (2020). *Zero trust architecture* (NIST Special Publication 800-207). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-207
