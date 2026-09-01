# Release Verification Gates

A release is eligible for merge only after the pull-request head passes the following independent gates:

1. **Source integrity:** Python compilation succeeds and package build creates a wheel.
2. **Deterministic behavior:** committed golden charts, Li Chun annual boundaries, `jie` monthly boundaries, daewoon direction, time policy, and lunar conversion tests pass. Solar-term objects are selected with an explicit `occurs_at` key so model ordering can never affect calendar results.
3. **Model orchestration contract:** offline Contextual Orchestrator tests prove gateway authentication, endpoint resolution, `model=orchestrator/free`, route/conduct metadata, absence of provider passthrough fields, transient retry, JSON parsing, schema validation, bounded same-route repair, direct-backend rejection, non-free-model rejection, and no direct-provider fallback.
4. **Editorial quality:** required chapters, constructive relationship guidance, explicit Korean copy, disclaimer, fingerprint fidelity, and forbidden-claim rules pass.
5. **Delivery:** API, queue, worker, HTML, PDF, JSON, path safety, deletion, and manifests pass.
6. **Static quality:** Ruff, public docstrings, document validation, prompt validation, product-gap/DDD architecture-fitness audit, and exactly 100% production statement/branch coverage pass.
7. **Test transport:** Starlette API tests use the maintained `httpx2` transport. Deprecation and resource warnings are release failures rather than accepted test noise.
8. **Security:** Security Scan and Semgrep pass, ordinary CI/release workflows receive no model credential, and the manual live lane receives only the Contextual Orchestrator gateway token and URL.
9. **Review:** reviewers inspect deterministic policy changes, privacy boundaries, orchestration/DDD boundaries, prompt changes, rendering impact, and failure states before merge.

Verification evidence belongs to the exact pull-request head. A previous green run is not sufficient after any source, dependency lock, prompt, architecture, or workflow change.

Live model evaluation is separately opt-in with `CONTEXTUAL_ORCHESTRATOR_TOKEN` and an approved gateway URL. It must exercise `orchestrator/free`, record only privacy-safe virtual-model/attempt/repair evidence, omit raw trace content, and never receive provider-native credentials. Hosted availability is supplementary evidence and does not replace deterministic or security gates.
