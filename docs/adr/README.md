# Architecture Decision Record Index

This directory is the authoritative index for durable Four Pillars architecture decisions. Chat transcripts, PR bodies, issue comments, generated plans, and temporary implementation notes may explain a decision but do not replace an ADR.

## Status model

- **Proposed** — under review; not an architecture requirement yet.
- **Accepted** — governs protected-main design until superseded.
- **Deprecated** — still supported temporarily but should not guide new design.
- **Superseded** — retained for history; a newer ADR is authoritative.

Architecture maturity such as `active_pr` is separate from ADR status. An Accepted ADR may govern both shipped and unmerged work without inventing an extra ADR status value.

When one ADR changes another, the newer record must name the prior record and the prior record must be updated to point to the successor when practical. A source change that contradicts an Accepted ADR requires a superseding ADR in the same or a prerequisite PR.

## Decision catalogue

| ADR | Status | Decision | Primary implementation/evidence |
|---|---|---|---|
| [0001-deterministic-core-and-nim-boundary.md](0001-deterministic-core-and-nim-boundary.md) | Accepted | Deterministic calculation is authoritative; AI receives immutable evidence. | `calendar.py`, `solar.py`, `fortune.py`, calculation fingerprint, quality tests |
| [0002-nvidia-nim.md](0002-nvidia-nim.md) | Accepted | Direct NVIDIA NIM is the standalone LLM generation/evaluation backend; ADR 0003 extends organization integration. | `nim.py`, settings, hosted/offline NIM tests |
| [0003-explicit-contextual-orchestrator-backend.md](0003-explicit-contextual-orchestrator-backend.md) | Accepted | Contextual Orchestrator is an explicit optional organization adapter with its own token and no silent fallback. | `contextual_orchestrator.py`, adapter tests, modularity docs |
| [0004-purpose-bound-personal-data.md](0004-purpose-bound-personal-data.md) | Accepted | Preserve necessary PII for the approved computation/interpretation purpose while limiting fields, access, retention, telemetry, and disclosure instead of blanket masking. | API/history redaction, public status schema, artifact UUIDs, retention/deletion, threat model |
| [0005-architecture-description-and-maturity.md](0005-architecture-description-and-maturity.md) | Accepted | Architecture claims use a canonical documentation graph and explicit maturity labels; protected-main evidence outranks plans and PR prose. | documentation audit, architecture docs, contract tests |
| [0006-calculation-evidence-provenance.md](0006-calculation-evidence-provenance.md) | Accepted | Solar-term/calendar changes require versioned astronomical policy plus independent boundary evidence rather than AI/app oracle correction. | `solar.py`, `calendar.py`, KASI/NAOJ fixtures, calculation doctoring |
| [0007-autonomous-development-authority.md](0007-autonomous-development-authority.md) | Accepted | Model development, credential-free verification, review, merge and release remain separate authorities; one PR/run is a safety bound, not an early-stop rule. | minute-17/minute-47 workflows; PR #29 is separately tracked as `active_pr` architecture evidence |

## Decisions that require a new ADR

A new or superseding ADR is normally required for changes to any of the following:

- calendar/timezone/solar-term/day-rollover source-of-truth policy;
- deterministic evidence or fingerprint semantics;
- interpretation provider or model-routing authority;
- personal-data processing purpose or external recipient;
- authentication/authorization boundary;
- durable schema ownership or migration strategy;
- job state machine, idempotency semantics, or recovery authority;
- artifact provenance or release-signing/provenance model;
- standalone versus MSA ownership boundary;
- autonomous development, review, merge, release, or deployment authority;
- supported scientific/quality claims or externally visible safety policy.

Small implementation choices that remain inside an Accepted ADR and preserve its observable contract do not need a new record.

## Review checklist

Every Accepted ADR should make the following discoverable:

1. context and decision drivers;
2. explicit decision and owner/bounded context;
3. allowed and forbidden dependencies;
4. security/privacy/credential implications;
5. failure, degraded-mode, and recovery behavior;
6. compatibility/migration/rollback implications when applicable;
7. test and operational evidence;
8. consequences and rejected alternatives;
9. reversal or supersession conditions;
10. relevant APA 7th standards/research references when the decision depends on external evidence.
