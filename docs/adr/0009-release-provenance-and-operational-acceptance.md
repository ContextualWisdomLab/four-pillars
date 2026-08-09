# ADR 0009: Release only from integrated protected main with verifiable provenance

- Status: Proposed
- Date: 2026-08-09

## Context and drivers

A green feature PR is not the same thing as a releasable product. Four Pillars has deterministic calculation policy, model/provider adapters, persistent job semantics, browser/API contracts, automation governance, documentation and supply-chain dependencies that can interact after integration. Releases also need traceable package artifacts that correspond to the exact protected-main source that passed the release gate.

The current `release.yml` already validates protected-main source, builds wheel/source distributions and a pinned runtime container, generates curated notes, publishes SHA-256 checksums, targets the release at the exact `GITHUB_SHA`, and treats an existing version as idempotently published. It does not yet publish a standardized SBOM/attestation/signature set; those remain a product-supply-chain gap.

## Decision

1. **Protected-main source only.** Version publication occurs only from `refs/heads/main` after the dedicated release validation job succeeds. Feature/draft branches never publish official versions.
2. **Integration acceptance.** Release validation repeats dependency integrity, product/documentation audit, lint/docstrings, compilation, prompt/docs checks, all offline tests with 100% production statement/branch coverage, package build, and pinned runtime-container build. Feature-PR checks are evidence, not a substitute for this integrated validation.
3. **SemVer and CHANGELOG alignment.** Public package, Python runtime, FastAPI application version, release test and dated CHANGELOG section must agree. Only actually integrated/shipped changes move out of Unreleased.
4. **Exact source target.** GitHub release/tag targets the exact protected-main `GITHUB_SHA` that produced the validated artifacts.
5. **Versioned artifacts.** Publish source distribution, wheel and `SHA256SUMS`. Release notes are curated from the matching CHANGELOG release section rather than generated from arbitrary commit messages.
6. **Idempotency.** If the exact version release already exists, publication exits without overwriting it. A different source must use a new version rather than replace an existing immutable release identity.
7. **No model credential in release quality.** Release validation/publication does not require `NVIDIA_NIM_API_KEY` or Contextual Orchestrator credentials. Hosted model evaluation is supplementary and cannot make deterministic release quality depend on an external provider.
8. **Operational acceptance before strong claims.** New scheduler/control-plane, migration, security/privacy, persistence or recovery capabilities require protected-main operational evidence appropriate to the change before documentation markets them as production-ready.
9. **Future provenance hardening.** SBOM, build provenance/attestation and artifact signing/verification are Planned. They must be added through a separately reviewed change and then become release requirements before this ADR can be Accepted as the complete intended provenance policy.

## Alternatives considered

### Publish from every green feature PR

Rejected because it bypasses integration validation, release-note/version coherence and protected-main authority.

### Overwrite a release when a packaging defect is found

Rejected because it destroys artifact provenance. Corrective releases use a new SemVer version.

### Require live LLM tests for every release

Rejected as the sole release dependency because hosted model availability/quotas can fail independently of code and deterministic calculation correctness. Bounded live evaluation remains an explicit supplementary gate where policy requires it.

## Consequences

- Release latency is slightly higher than direct branch publication.
- Integrated main can remain ahead of the last released version until a coherent release bump is reviewed.
- Supply-chain assurance improves through exact source/artifact/checksum linkage, but current checksums are not equivalent to signed provenance or an SBOM.

## Failure and recovery

If validation fails, nothing publishes. If artifact construction fails, the release is not created. If release publication partially fails before GitHub records the release, rerun against the same exact main/version after diagnosing the failure. If the version already exists, do not replace assets automatically; inspect the existing release and create a corrective version if artifacts/source differ.

A rollback of deployed service behavior uses an already verified prior release/artifact rather than rebuilding a historical tag under current dependencies.

## Security and governance impact

Release publication has a dedicated job with `contents: write`; validation stays read-only. Secrets for model development/review are not required by release publication. Supply-chain hardening should progressively add SBOM/provenance/signing without widening model/reviewer authority.

## Acceptance evidence

Before this ADR becomes Accepted:

- current version/changelog/release tests remain machine-checkable;
- protected-main release validation proves package/container artifacts from the exact source;
- published source/wheel/checksum assets are independently verified after release;
- SBOM is produced for release artifacts or the accepted scope explicitly documents why not;
- provenance/attestation and artifact-signing decision is implemented or explicitly superseded by an accepted alternative;
- migration/recovery/control-plane releases include appropriate protected-main operational acceptance evidence.

## Migration and rollback

Existing release workflow remains compatible. Future SBOM/provenance/signature assets are additive until declared mandatory. Once mandatory, rollback of the release workflow must not permit unsigned/unprovenanced artifacts to masquerade as satisfying the later policy.

## Supersession conditions

Supersede this ADR if the organization adopts a central release/provenance service that provides equal or stronger exact-source binding, immutable versioning, validation, SBOM/provenance/signing and rollback evidence through a documented versioned integration.
