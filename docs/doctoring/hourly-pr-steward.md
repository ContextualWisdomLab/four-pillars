# Hourly governed pull-request steward — evidence doctoring

## Claim boundary

The steward automates bounded repository maintenance. It does not prove semantic correctness, replace independent review, establish that an LLM repair is safe, or grant a model authority to approve, merge, release, or deploy. GitHub branch protection, required reviews, unresolved-conversation policy, exact-head Checks, deterministic tests, security scanning, and human escalation remain authoritative.

A successful artifact digest proves identity, not meaning. A successful test suite proves only the encoded test contract. Automated review can miss defects or produce false positives. LLM-generated changes remain untrusted until a fresh credential-free verifier executes the exact patch and normal repository governance accepts the resulting head.

## Source-to-control trace

| Design decision | Evidence | Implemented control |
|---|---|---|
| Keep generated changes inside normal pull-request governance | GitHub protected-branch and auto-merge documentation | The steward uses normal squash auto-merge without `--admin`; required reviews and Checks cannot be bypassed. |
| Use short-lived, least-privilege publication credentials | GitHub App authentication and Actions hardening documentation | The existing repository-scoped maintainer App token is minted only in non-model publisher/merge jobs. |
| Treat build inputs and automation outputs as untrusted | GitHub Actions security hardening; NIST SP 800-218 | Review and Check data is schema-validated, byte-bounded, Unicode-normalized, and passed as data. Proposed code runs only on an ephemeral verifier without model or publication credentials. |
| Separate preparation, verification, and release authority | NIST SP 800-218; ISO/IEC 42001:2023; ISO/IEC 23894:2023 | Read-only inspection, model proposal, fresh verification, publication, and merge are separate jobs and credentials. |
| Allocate model computation to bounded task complexity | Fugu; Conductor; TRINITY | A single bounded repair defaults to one routed model; explicit stages, access lists, bounded recursion, and role-specific effort are required before deeper orchestration. |
| Preserve deterministic evidence above generated narrative | Existing Four Pillars calculation architecture and quality gates | The steward may repair code and tests but cannot override exact chart facts, fingerprints, date boundaries, or quality policy. |
| Preserve complete release evidence | ISO/IEC 25010:2023 quality characteristics and existing project policy | Every repair runs dependency, product-gap, lint/docstring, compile, document/prompt, 100% statement/branch coverage, package, container, security, and SAST gates. |

## GitHub governance reviewed

GitHub auto-merge waits for branch-protection requirements and required Checks before completing a merge. The steward therefore queues auto-merge rather than polling until it can perform an administrative merge. The workflow never uses `--admin`, never submits an approval, and never dismisses a review.

GitHub App installation access tokens are short-lived and limited by both the App installation and the permissions requested by the workflow. The steward reuses the established Four Pillars maintainer App identity and requests only repository contents and pull-request mutation required for a fast-forward repair push or governed auto-merge. It does not rename or repurpose existing review-agent credentials.

GitHub warns that pull-request content, issue text, branch names, workflow outputs, and contributed code can be attacker-controlled. The inspector therefore does not interpolate review bodies into shell syntax. It writes strict JSON through `scripts/prepare_pr_steward_evidence.py`; OpenCode receives that file only after GitHub, OIDC, Actions runtime/cache, and command-file channels have been removed.

## Orchestration research application

**Fugu.** Fugu motivates selecting between direct model use and deeper coordinated execution rather than applying one expensive strategy to every task. One PR repair is intentionally bounded and starts with single-model routing. More agents are not treated as automatically safer or better.

**Conductor.** Conductor motivates explicit task decomposition, access lists, and controlled delegation. The steward fixes the workflow stages and denies task delegation inside OpenCode. Any future contextual-orchestrator integration must preserve the same evidence and credential boundaries.

**TRINITY.** TRINITY motivates specialized thinker, worker, verifier, and synthesis roles. In this workflow the model is only a worker/proposer; deterministic verification and GitHub governance are independent roles. Reasoning effort may vary by role, but private chain-of-thought is never stored as operational evidence.

These research systems support design hypotheses, not a claim that multi-agent orchestration improves every repair. Ablation must compare a routed single model with bounded conducted execution using exact same tasks, tests, provider-reported usage, failure rates, and human review outcomes. Speed is not the optimization target, but bounded cost and reproducibility remain governance requirements.

## Operational evidence limits

The evidence artifact contains only allow-listed pull-request identity, bounded title/body text, submitted reviews, unresolved review threads, and exact-head Check summaries. It excludes API keys, workflow tokens, environment values, user birth data, generated reports, model traces, artifact paths, and unrelated issue content. URLs are restricted to HTTPS GitHub hosts. UTF-8 byte limits apply after normalization.

A same-repository branch is required for automated repair because the repository-scoped App cannot safely claim ownership of a contributor fork. External-fork PRs remain reviewable but require a maintainer or contributor to push the repair.

## Residual risks

- A verifier has ordinary network egress unless GitHub-hosted runner networking is separately constrained.
- A malicious test can consume resources or probe the ephemeral runner; timeouts, secret removal, and fresh runners reduce but do not eliminate this risk.
- Review comments may contain prompt injection. Schema validation and explicit untrusted-data instructions reduce risk but do not prove model obedience.
- Repository App compromise would affect publication authority; short-lived tokens and late minting reduce exposure but do not replace App key rotation and audit.
- GitHub API or review-agent outages can delay merges. The workflow fails closed and tries again next hour.
- Check success can coexist with untested behavior. Realistic domain fixtures and independent review remain mandatory.

## APA 7th references

GitHub. (n.d.-a). *About protected branches*. GitHub Docs. Retrieved August 7, 2026, from https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

GitHub. (n.d.-b). *Automatically merging a pull request*. GitHub Docs. Retrieved August 7, 2026, from https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request

GitHub. (n.d.-c). *Making authenticated API requests with a GitHub App in a GitHub Actions workflow*. GitHub Docs. Retrieved August 7, 2026, from https://docs.github.com/en/apps/creating-github-apps/writing-code-for-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow

GitHub. (n.d.-d). *Security hardening for GitHub Actions*. GitHub Docs. Retrieved August 7, 2026, from https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

International Organization for Standardization. (2023a). *ISO/IEC 23894:2023 Information technology—Artificial intelligence—Guidance on risk management*. https://www.iso.org/standard/77304.html

International Organization for Standardization. (2023b). *ISO/IEC 42001:2023 Information technology—Artificial intelligence—Management system*. https://www.iso.org/standard/42001.html

International Organization for Standardization. (2023c). *ISO/IEC 25010:2023 Systems and software engineering—Systems and software quality requirements and evaluation (SQuaRE)—Product quality model*. https://www.iso.org/standard/78176.html

National Institute of Standards and Technology. (2022). *Secure software development framework (SSDF) version 1.1: Recommendations for mitigating the risk of software vulnerabilities* (NIST SP 800-218). https://doi.org/10.6028/NIST.SP.800-218

Nielsen, S., Cetin, E., Schwendeman, P., Sun, Q., Xu, J., & Tang, Y. (2025). *Learning to orchestrate agents in natural language with the Conductor* [Preprint]. arXiv. https://arxiv.org/abs/2512.04388

NVIDIA. (n.d.). *NVIDIA NIM for large language models documentation*. Retrieved August 7, 2026, from https://docs.nvidia.com/nim/large-language-models/latest/

OpenCode. (n.d.). *OpenCode documentation*. Retrieved August 7, 2026, from https://opencode.ai/docs/

Sakana AI. (2026, June 22). *Sakana Fugu: One model to command them all*. https://sakana.ai/fugu-release/

Xu, J., Sun, Q., Schwendeman, P., Nielsen, S., Cetin, E., & Tang, Y. (2025). *TRINITY: An evolved LLM coordinator* [Preprint]. arXiv. https://arxiv.org/abs/2512.04695
