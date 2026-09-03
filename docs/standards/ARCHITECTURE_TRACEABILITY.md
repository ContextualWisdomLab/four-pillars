# Architecture Requirement Traceability

This matrix connects the product/technical requirements emphasized across Four Pillars development to protected-main implementation evidence, architecture decisions, tests, operations, and residual gaps. It supplements the broader `TRACEABILITY.md` rather than replacing it.

| Requirement / invariant | Product / technical source | Decision / architecture | Implementation / evidence | Residual gap or trigger |
|---|---|---|---|---|
| Deterministic calculation is authoritative | PRD 4.1; TRD 3 | ADR 0001; ADR 0006 | `calendar.py`, `solar.py`, `fortune.py`, fingerprint, KASI/NAOJ fixtures | extend independent evidence before broad historical-precision claims |
| Precise year/month boundaries | PRD 4.1–4.2; TRD 3 | ADR 0006 | all 2026 `jie` fixtures; Li Chun/`jie` transition tests; calculation `calendar-1.1.0` | historical/time-scale/timezone scope remains explicit |
| AI cannot rewrite calculated facts | PRD 4.3–4.4; TRD 4–5 | ADR 0001 | Pydantic schemas, fingerprint quality gate, bounded editorial repair | continue regression coverage for new prompt schemas |
| Direct NVIDIA NIM standalone path | PRD 4.3; TRD 4 | ADR 0002 | `NimClient`, `NVIDIA_NIM_API_KEY`, offline/live contract tests | hosted model availability is account-dependent |
| Explicit Contextual Orchestrator path | PRD 4.3/4.7; TRD 4/13 | ADR 0003 | orchestrator adapter, separate token, prompt-safe attribution | gateway operational controls are external dependency evidence |
| No silent provider fallback | PRD 4.3; TRD 4/11 | ADR 0002–0003 | selection/settings and terminal failure tests | any future fallback requires a superseding ADR |
| Purpose-bound personal data, no blanket masking | PRD 4.8; TRD 10 | ADR 0004 | redacted history, UUID artifacts, attribution controls, retention/deletion | deployment legal basis/subprocessor contracts remain operator-specific |
| Durable async report queue | PRD 4.5; TRD 6–7 | DATA_MODEL | `report_jobs`, atomic claim/create, lifecycle tests | multi-node adapter is planned |
| Safe idempotency | PRD 4.6; TRD 6.4 | DATA_MODEL | request fingerprint, key digest, unique partial index, concurrency tests | remote adapters need equivalent atomicity |
| Privacy-safe job history | PRD 4.5; TRD 6.3/8 | ADR 0004; DATA_MODEL | strict cursor, stable `(created_at,id)` order, redaction tests | tenant authorization if tenancy is added |
| Searchable Korean HTML/PDF with integrity manifest | PRD 4.5; TRD 9 | SYSTEM_ARCHITECTURE | `reporting.py`, manifest hashes, rendering tests | visual template changes require Visual Inspection/Figma sync |
| Standalone + modular MSA | PRD 4.7; TRD 13 | SYSTEM_ARCHITECTURE; MODULARITY | structural ports, injected interpreter/repository/publisher | no direct cross-service DB access; concrete remote adapters need their own tests |
| Exact 100% owned production statement/branch coverage | PRD 5; TRD 15 | TEST_STRATEGY | CI/pytest-cov gates | coverage is necessary, not sufficient, evidence |
| Public docstrings are beginner-readable | PRD 5; TRD 15 | TEST_STRATEGY | repository docstring checks | review semantic usefulness, not only presence |
| Work-conserving autonomous development | PRD 4.9; TRD 14 | ADR 0007; AUTONOMOUS_DEVELOPMENT | minute-47 product-dev control; exact-head governance | PR #29 steward is `superseded`; any successor needs fresh evidence |
| NVIDIA model credential only for scheduled dev | TRD 14 | ADR 0007 | `NVIDIA_NIM_API_KEY`; no `COPILOT_GITHUB_TOKEN` | preserve reviewer key chain independently |
| Architecture claims distinguish shipped vs planned | PRD 4.9; TRD 16 | ADR 0005; DOCUMENTATION_AUDIT | documentation architecture contract test | PR #29 is `superseded`; future proposals need their own classification |
| Threat/security/privacy model is explicit | PRD 4.8; TRD 10 | THREAT_MODEL; ADR 0004/0007 | security tests, secret separation, artifact/history controls | certification/attestation requires deployed-org evidence |
| Backup/restore/retention/incident ownership | PRD 5; TRD 11 | OPERABILITY | standalone runbook + operability acceptance expectations | automated restore drills/multi-node DR are deployment work |
| APA 7 / current primary evidence | PRD 4.9; TRD 17 | doctoring + references | canonical architecture doctoring, broader standards references | review on standard revision/provider architecture change |

## Maturity rule

PR #29 references are `superseded` because it closed without merge. Another open change remains `active_pr`. A merge commit alone does not establish an operational claim when the feature's acceptance requires a protected-main scheduled/manual run. The architecture documentation must be updated from `active_pr` to `implemented_on_protected_main` only after the required evidence exists.
