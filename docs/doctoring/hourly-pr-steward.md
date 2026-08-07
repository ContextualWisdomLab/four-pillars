# Hourly exact-head pull-request steward — evidence doctoring

## Claim boundary

The steward automates bounded repository maintenance. It does not prove semantic
correctness, replace independent review, establish that an LLM repair is safe,
or grant a model authority to approve, merge, release, or deploy. GitHub branch
protection, required reviews, unresolved-conversation policy, exact-head Checks,
deterministic tests, security scanning, and human escalation remain authoritative.

A successful digest proves artifact identity, not meaning. A successful test
suite proves only the encoded test contract. Automated review can miss defects
or produce false positives. LLM-generated changes remain untrusted until a fresh
credential-free verifier executes the exact patch and ordinary repository
governance accepts the resulting head.

The controls described here support future CSAP and SOC 2 readiness. Four
Pillars has not undergone the required independent assessment, and this document
is **not a certification**, attestation, audit report, legal opinion, or claim of
conformity with CSAP, SOC 2, ISO/IEC 42001, ISO/IEC 23894, or NIST publications.

## Source-to-control trace

| Design decision | Evidence | Implemented control |
|---|---|---|
| Keep generated changes inside normal PR governance | GitHub protected-branch and auto-merge documentation | The steward queues normal squash auto-merge with an exact-head match and never uses `--admin`, submits approval, dismisses review, tags, releases, or deploys. |
| Use short-lived, least-privilege mutation credentials | GitHub App authentication and Actions hardening documentation | The established repository-scoped Maintainer App token is minted only in non-model publisher/merge jobs after immutable evidence revalidation. |
| Treat build inputs and automation outputs as untrusted | GitHub Actions hardening; NIST SP 800-218; NIST SP 800-218A | Review/Check data is schema-validated, byte-bounded, Unicode-normalized, and explicitly labelled untrusted. Proposed code executes only on a fresh verifier without model or publication credentials. |
| Separate preparation, verification, and authority | NIST SP 800-218/218A; ISO/IEC 42001:2023; ISO/IEC 23894:2023 | Read-only inspection, NIM-only proposal, fresh verification, non-executing publication, and governed merge are separate jobs and credential zones. |
| Preserve operational evidence without blanket PII masking | CSAP scope/evidence framing; AICPA Trust Services Criteria privacy/confidentiality concepts | Evidence is purpose-limited to one PR and excludes birth inputs, customer records, report content, emails, credentials, environment values, production artifacts, and unrelated issues. Useful Korean diagnostics remain readable. |
| Keep evidence available only as long as needed | GitHub Actions artifact controls; minimization and retention principles | Evidence and repair artifacts use **one-day retention** and owner-only canonical JSON before upload. |
| Allocate model compute to bounded task complexity | Fugu; Conductor; TRINITY | One exact-head repair starts as one routed worker. Selection, verification, publication, and merge remain deterministic roles. Deeper conduct requires a separately reviewed ablation. |
| Preserve deterministic facts above generated narrative | Existing Four Pillars calculation architecture | The steward may repair code/tests but cannot override chart facts, fingerprints, calendar boundaries, or quality policy. |
| Preserve complete release evidence | ISO/IEC 25010:2023 and project release policy | Every repair runs both Python lanes, product-gap, lint/docstring, compile, document/prompt, 100% statement/branch coverage, package, container, security, and SAST gates. |

## Current standards status reviewed on 2026-08-07

NIST SP 800-218 Version 1.1 remains the final SSDF publication. NIST published
SP 800-218 Rev. 1 as the initial public draft of SSDF Version 1.2 on December 17,
2025; the public-comment period is closed, so the draft is informative rather
than a final compliance baseline. NIST SP 800-218A is final and augments SSDF
with AI-model-development practices. The steward therefore cites final SP
800-218 and SP 800-218A as normative engineering guidance and tracks the 1.2
draft for future reviewed adoption.

KISA describes CSAP as a statutory certification process for covered cloud
services and publishes formal assessment, remediation, committee, certificate,
and recurring-surveillance steps. Engineering documentation can prepare control
evidence, but only the designated assessment and certification process can
issue CSAP certification.

AICPA describes SOC 2 as an examination of a service organization's system and
controls relevant to security, availability, processing integrity,
confidentiality, or privacy. The 2017 Trust Services Criteria with revised 2022
points of focus are criteria for attestation or consulting engagements. Internal
checklists or automation cannot self-issue a SOC 2 report.

## GitHub governance reviewed

GitHub auto-merge waits for configured branch-protection and required Check
conditions. The steward therefore queues auto-merge rather than polling until it
can perform an administrative merge. It never submits approval or dismisses a
review.

GitHub App installation tokens are short-lived and limited by both the App
installation and requested permissions. The steward reuses the established Four
Pillars Maintainer App identity and requests only repository contents and
pull-request mutation needed for one normal repair push or governed merge. It
does not rename, reuse, or expose existing reviewer-agent credentials.

Pull-request bodies, review text, branch names, workflow outputs, logs, and
contributed code can be attacker controlled. The inspector never interpolates
review bodies into shell syntax. A trusted standard-library parser canonicalizes
strict JSON. OpenCode receives that evidence only after GitHub, OIDC, Actions
runtime/cache, command-file, reviewer, and publication channels are removed.

## PII and confidentiality alternative to blanket masking

PII masking is not used as a universal control because indiscriminate redaction
would destroy code paths, Korean diagnostics, stack traces, and reviewer context
needed to repair failures. The replacement control set is:

1. **Purpose limitation:** only exact PR identity, review states/threads, Check
   states, and bounded failed-job logs.
2. **Data exclusion:** no customer birth data, user context, generated reports,
   model traces, artifact paths, email addresses, API keys, tokens, environment
   dumps, or unrelated issue content.
3. **Least privilege:** read-only inspector, `NVIDIA_NIM_API_KEY`-only proposer,
   uncredentialed verifier, and late repository-scoped App token.
4. **Content controls:** strict schemas, allow-listed URLs/identifiers, Unicode
   normalization, control/bidirectional removal, byte/item caps, symlink and
   gitlink rejection, and credential-looking log-line redaction.
5. **Retention:** one-day retention for evidence and repair artifacts.
6. **Integrity and audit:** exact head/base, numeric artifact ID, server digest,
   patch SHA-256, file/byte counts, Git modes, normal commits, review history,
   and GitHub Actions logs.
7. **Change management:** no force push, self-approval, review dismissal,
   administrative merge, tag, release, or deployment.

## Orchestration research application

**Fugu.** Fugu motivates routing between direct model use and deeper coordinated
execution rather than applying one expensive pattern to every task. One bounded
repair defaults to a single routed worker.

**Conductor.** Conductor motivates explicit decomposition, access lists, and
controlled delegation. The steward fixes stages and denies task delegation
inside OpenCode. Any future contextual-orchestrator adapter must preserve the
same evidence and credential boundaries.

**TRINITY.** TRINITY motivates specialized thinker, worker, verifier, and
synthesis roles. Here the model is only a worker/proposer; deterministic
selection, verification, publication, and GitHub governance are independent
roles. Private chain-of-thought is not operational evidence.

These sources support design hypotheses, not a claim that multi-agent
orchestration improves every repair. A future ablation must compare routed and
bounded-conducted execution on the same PR fixtures, tests, provider-reported
usage, failure rates, review outcomes, and security findings. Speed is not the
optimization target, but cost bounds and reproducibility remain mandatory.

## Residual risks

- The ephemeral verifier has ordinary network egress unless runner networking is
  separately constrained.
- Malicious tests may consume resources or probe the runner; timeouts, secret
  removal, and fresh runners reduce but do not eliminate the risk.
- Prompt injection may be present in reviews or failed logs; schema validation
  and explicit untrusted-data boundaries do not prove model obedience.
- Compromise of the repository Maintainer App remains a publication risk; late,
  short-lived tokens do not replace key rotation, installation review, and audit.
- GitHub API, runner, or reviewer outages can delay merge; unknown state fails
  closed and is observed again on the next hourly run.
- Green Checks can coexist with untested behavior; realistic domain fixtures and
  independent review remain mandatory.
- `semgrep scan --config auto` may use remote rule resolution when locally
  available; repository-required SAST remains the authoritative post-publication
  exact-head Check.

## Research-service limitation

Consensus was queried on 2026-08-07 for recent autonomous secure-software-agent
research, but the connected account reported its monthly quota exhausted. No
paper result from that query is represented as evidence. Primary official
sources and the repository's already catalogued Fugu, Conductor, and TRINITY
sources were used instead.

## APA 7th references

American Institute of Certified Public Accountants. (2023). *2017 trust services
criteria for security, availability, processing integrity, confidentiality, and
privacy (with revised points of focus—2022)*. AICPA & CIMA.
https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022

Booth, H., Ogata, M., Kent, K., Souppaya, M., & Dodson, D. (2025). *Secure
software development framework (SSDF) version 1.2: Recommendations for mitigating
the risk of software vulnerabilities* (NIST SP 800-218 Rev. 1, Initial Public
Draft). National Institute of Standards and Technology.
https://csrc.nist.gov/pubs/sp/800/218/r1/ipd

Booth, H., Souppaya, M., Vassilev, A., Ogata, M., Stanley, M., & Scarfone, K.
(2024). *Secure software development practices for generative AI and dual-use
foundation models: An SSDF community profile* (NIST SP 800-218A). National
Institute of Standards and Technology. https://doi.org/10.6028/NIST.SP.800-218A

GitHub. (n.d.-a). *About protected branches*. GitHub Docs. Retrieved August 7,
2026, from https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

GitHub. (n.d.-b). *Automatically merging a pull request*. GitHub Docs. Retrieved
August 7, 2026, from https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request

GitHub. (n.d.-c). *Making authenticated API requests with a GitHub App in a
GitHub Actions workflow*. GitHub Docs. Retrieved August 7, 2026, from
https://docs.github.com/en/apps/creating-github-apps/writing-code-for-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow

GitHub. (n.d.-d). *Security hardening for GitHub Actions*. GitHub Docs.
Retrieved August 7, 2026, from
https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions

International Organization for Standardization. (2023a). *ISO/IEC 23894:2023
Information technology—Artificial intelligence—Guidance on risk management*.
https://www.iso.org/standard/77304.html

International Organization for Standardization. (2023b). *ISO/IEC 42001:2023
Information technology—Artificial intelligence—Management system*.
https://www.iso.org/standard/42001.html

International Organization for Standardization. (2023c). *ISO/IEC 25010:2023
Systems and software engineering—Systems and software quality requirements and
evaluation (SQuaRE)—Product quality model*.
https://www.iso.org/standard/78176.html

Korea Internet & Security Agency. (2025). *2025년 클라우드서비스 보안인증제도
안내서*. https://isms.kisa.or.kr/main/csap/notice

Korea Internet & Security Agency. (n.d.). *클라우드 보안인증제 제도소개*.
Retrieved August 7, 2026, from https://isms.kisa.or.kr/main/csap/intro/index.jsp

National Institute of Standards and Technology. (2022). *Secure software
development framework (SSDF) version 1.1: Recommendations for mitigating the risk
of software vulnerabilities* (NIST SP 800-218).
https://doi.org/10.6028/NIST.SP.800-218

Nielsen, S., Cetin, E., Schwendeman, P., Sun, Q., Xu, J., & Tang, Y. (2025).
*Learning to orchestrate agents in natural language with the Conductor*
[Preprint]. arXiv. https://arxiv.org/abs/2512.04388

NVIDIA. (n.d.). *NVIDIA NIM for large language models documentation*. Retrieved
August 7, 2026, from https://docs.nvidia.com/nim/large-language-models/latest/

OpenCode. (n.d.). *OpenCode documentation*. Retrieved August 7, 2026, from
https://opencode.ai/docs/

Sakana AI. (2026, June 22). *Sakana Fugu: One model to command them all*.
https://sakana.ai/fugu-release/

Xu, J., Sun, Q., Schwendeman, P., Nielsen, S., Cetin, E., & Tang, Y. (2025).
*TRINITY: An evolved LLM coordinator* [Preprint]. arXiv.
https://arxiv.org/abs/2512.04695
