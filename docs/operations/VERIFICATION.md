# Release Verification Gates

A release is eligible for merge only after the pull-request head passes the following independent gates:

1. **Source integrity:** Python compilation succeeds and package build creates a wheel.
2. **Deterministic behavior:** committed golden charts, Li Chun annual boundaries, `jie` monthly boundaries, daewoon direction, time policy, and lunar conversion tests pass. Solar-term objects are selected with an explicit `occurs_at` key so model ordering can never affect calendar results.
3. **AI contract:** mocked NVIDIA NIM tests prove authentication, endpoint resolution, transient retry, JSON parsing, schema validation, and bounded repair. Hosted tests are separately opt-in with `NVIDIA_API_KEY`.
4. **Editorial quality:** required chapters, constructive relationship guidance, explicit Korean copy, disclaimer, fingerprint fidelity, and forbidden-claim rules pass.
5. **Delivery:** API, queue, worker, HTML, PDF, JSON, path safety, deletion, and manifests pass.
6. **Static quality:** Ruff, document validation, prompt validation, and coverage at or above the configured threshold pass.
7. **Review:** reviewers inspect deterministic policy changes, privacy boundaries, prompt changes, rendering impact, and failure states before merge.

Verification evidence belongs to the exact pull-request head. A previous green run is not sufficient after any source or prompt change. Live NIM evaluation records the configured model and prompt hashes because free hosted model availability may change independently of source code.
