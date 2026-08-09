# ADR 0005: Code-current documentation is an architectural authority surface

- Status: Proposed
- Date: 2026-08-09

## Context and drivers

Four Pillars now spans deterministic astronomical/calendar calculation, symbolic fortune derivation, model-backed interpretation, quality control, asynchronous jobs, browser recovery, release automation, and autonomous repository control planes. Historical implementation plans and pull-request bodies contain useful rationale, but they are not reliable current architecture: files can move, implementation semantics can change, and an old PR can describe a head that no longer exists.

ISO/IEC/IEEE 42010:2022 requires architecture descriptions to express architecture through explicit architectural concepts, viewpoints and model kinds. ISO/IEC/IEEE 29148:2018 defines requirements-engineering information items and remains the current published edition during this review, although an Edition 3 DIS is under development. OMG UML 2.5.1 remains the formal UML specification used as notation guidance for committed diagrams.

The repository therefore needs one discoverable, code-current documentation graph rather than a collection of isolated prose files.

## Decision

Four Pillars shall treat authoritative documentation as a versioned product interface.

### Canonical surfaces

The repository maintains, at minimum:

- product requirements (`docs/product/PRD.md`);
- technical requirements (`docs/technical/TRD.md`);
- root architecture (`ARCHITECTURE.md`);
- ADR index and numbered decisions (`docs/adr/README.md`);
- UML/behavior/control-plane diagrams (`docs/uml/`);
- conceptual/logical data model (`docs/erd/`);
- API, calculation and modularity contracts (`docs/technical/`);
- privacy/data governance and security/control boundaries (`docs/security/`, `SECURITY.md`);
- compliance-readiness mappings (`docs/compliance/`);
- standards/research references and traceability (`docs/standards/`, `docs/doctoring/`);
- operations/recovery/runbooks (`docs/operations/`);
- UI source-of-truth references (`docs/design/`);
- agent/operator repository contracts (`AGENTS.md`, `CLAUDE.md`);
- release history (`CHANGELOG.md`).

`docs/architecture/DOCUMENTATION_MAP.md` defines the canonical graph and update triggers.

### Authority and conflict handling

Protected-main code and executable tests define implemented behavior. Accepted ADRs define intentional architectural constraints. PRD/TRD/public contracts define released requirements. Architecture/UML/ERD/security/operations documents explain current design. Doctoring explains external evidence and claim boundaries. Historical specs, plans, PR bodies and conversations remain history.

If these disagree, the disagreement is a repository defect. Documentation must be corrected or an intentional code/decision change must be made through a reviewed PR; maintainers must not silently reinterpret the conflict.

### Current, Proposed and Planned

Every material document distinguishes:

- **Implemented / Current** — present on protected main;
- **Accepted architecture** — intentional decision that governs implementation;
- **Proposed** — under review or dependent on an unmerged PR;
- **Planned** — intended future work without an accepted implementation.

A diagram may include Proposed/Planned elements only when they are visibly marked.

### Machine-checkable documentation contracts

Where practical, CI should verify required canonical files, ADR index links/statuses, documentation links, schema/version identifiers, current product names, and high-risk contractual assertions such as credential names or calculation evidence versions. Tests must not hard-code transient SHAs as timeless architecture.

## Alternatives considered

### Keep README plus PR bodies as sufficient documentation

Rejected because it forces future maintainers to reconstruct design from ephemeral review history and makes current-vs-historical claims ambiguous.

### Maintain only PRD/TRD

Rejected because product and technical requirements do not substitute for architecture decisions, persistence/data authority, trust boundaries, operational recovery, diagrams, or release evidence.

### Generate all documentation automatically from code

Rejected as the sole strategy because code cannot derive stakeholder concerns, rejected alternatives, risk acceptance, privacy purpose, operational ownership, or why a boundary exists. Generated references may supplement but not replace architectural decisions.

## Consequences

- Material changes require a documentation impact check.
- Documentation defects can block release when they misstate public/security/calculation contracts.
- The repository gains more files, but each has a bounded authority and update trigger.
- New engineers can reconstruct system behavior without chat history.

## Failure and recovery

A stale or contradictory document does not automatically change production behavior. It creates a fail-closed review obligation: identify the code-current behavior, classify whether code or documentation is wrong, repair through a normal PR, and update any dependent ADR/traceability links. If an ADR is wrong because the architecture decision changed, create a superseding ADR rather than rewriting history.

## Security and governance impact

Security/privacy controls are especially sensitive to stale documentation. Credential names, provider fallback policy, automation write authority, public-data redaction/purpose boundaries, and release gates must be compared against live code/workflows. Documentation itself must not contain real credentials, personal report data, or durable secret material.

## Acceptance evidence

Before this ADR becomes Accepted:

- canonical PRD/TRD/Architecture/ADR/UML/ERD/security/compliance/operations/traceability surfaces exist and cross-link;
- the known Contextual Orchestrator `native_json_mode` documentation contradiction is removed;
- proposed PR-steward behavior is clearly marked Proposed until merged;
- CI has at least lightweight checks for canonical document presence and ADR index integrity;
- the documentation map identifies current update triggers and ownership.

## Migration and rollback

This is additive documentation governance. Existing historical plans/specs are retained for provenance but lose implicit authority. If the documentation graph proves too fragmented, files may be consolidated through a later ADR as long as the required concerns and traceability remain explicit.

## Supersession conditions

Supersede this ADR if the repository adopts another independently reviewable architecture-description/requirements system that preserves equivalent authority, traceability, current-vs-proposed status, and machine-verifiable consistency.

## References

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2022). *Software, systems and enterprise—Architecture description* (ISO/IEC/IEEE Standard No. 42010:2022). https://www.iso.org/standard/74393.html

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2018). *Systems and software engineering—Life cycle processes—Requirements engineering* (ISO/IEC/IEEE Standard No. 29148:2018). https://www.iso.org/standard/72089.html

Object Management Group. (2017). *OMG Unified Modeling Language (OMG UML), version 2.5.1*. https://www.omg.org/spec/UML/2.5.1
