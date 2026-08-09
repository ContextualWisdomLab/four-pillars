# Four Pillars Repository Control-Plane Diagrams

This file complements `docs/uml/architecture.md` with repository-development and governance views. Implemented and Proposed zones are deliberately separated so an unmerged workflow is never presented as protected-main behavior.

Notation uses Mermaid in a UML-like manner. OMG UML 2.5.1 is the notation reference; ISO/IEC/IEEE 42010:2022 informs the separation of viewpoints and stakeholder concerns.

## Control-plane component view

```mermaid
flowchart LR
    Main[(Protected main)]
    Sentinel[Minute-17 quality sentinel\nImplemented]
    ProductDev[Minute-47 NVIDIA/OpenCode product developer\nImplemented]
    Steward[Minute-07 PR steward\nProposed]
    PR[Pull request]
    Checks[CI / Security / SAST / package checks]
    Review[Independent review agents / humans]
    Merge[Governed merge authority]
    Release[Protected-main release workflow]
    NIM[NVIDIA NIM\nNVIDIA_NIM_API_KEY]

    Main --> Sentinel
    Main --> ProductDev
    ProductDev -->|model call only| NIM
    ProductDev -->|bounded proposal PR| PR
    PR --> Checks
    PR --> Review
    PR -. inspected/repaired if merged .-> Steward
    Steward -. expected-head merge queue only if gates satisfied .-> Merge
    Checks --> Merge
    Review --> Merge
    Merge --> Main
    Main --> Release

    ProductDev -. no approval / merge / release authority .-> Merge
    NIM -. no GitHub write/reviewer authority .-> PR
```

`Steward` remains Proposed until its feature PR reaches protected main.

## Minute-47 product-development sequence — Implemented

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant G as Deterministic queue gate
    participant P as Proposal runner
    participant N as NVIDIA NIM/OpenCode
    participant A as Immutable proposal artifact
    participant V as Fresh verifier
    participant B as Fresh publisher
    participant App as Maintainer GitHub App
    participant GH as GitHub PR

    S->>G: hourly minute 47 / manual dispatch
    G->>G: verify repository + zero-open-PR + configured path
    alt gate not eligible
        G-->>S: deterministic exit reason
    else eligible
        G->>P: exact protected-main source
        P->>N: bounded task with NVIDIA_NIM_API_KEY only
        N-->>P: working-tree proposal
        P->>P: reject symlink/gitlink, bound files/bytes
        P->>A: full-index patch + SHA-256 + artifact identity
        A->>V: exact artifact
        V->>V: verify artifact/base/digest and apply
        V->>V: run release-quality tests with no model/publication credential
        A->>B: same exact artifact
        B->>B: verify without executing proposed code
        B->>B: parse bounded untrusted PR metadata
        B->>App: late-mint repository-scoped publication token
        App-->>B: short-lived publication authority
        B->>B: revalidate live main + zero-open-PR state
        B->>GH: create one branch and one PR
    end
```

The model path does not receive reviewer, merge or release authority. Publication credentials exist only after proposal verification.

## Minute-17 quality sentinel — Implemented

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant Q as Quality workflow
    participant T as Deterministic tests
    participant D as Documentation/product-gap audit
    participant I as Regression issue state

    S->>Q: hourly minute 17 / manual dispatch
    Q->>T: dependency integrity + lint + compile + docs/prompts + offline tests + 100% coverage + package
    Q->>D: deterministic product/documentation contract audit
    alt release-quality regression
        Q->>I: create/update one idempotent regression record
    else recovered
        Q->>I: close existing regression record with evidence
    end
```

The sentinel is intentionally model-free and receives no NIM credential.

## Minute-07 PR steward — Proposed

```mermaid
sequenceDiagram
    participant S as Scheduler
    participant I as Read-only PR inspector
    participant E as Evidence classifier
    participant R as Isolated repair runner
    participant N as NVIDIA NIM/OpenCode
    participant V as Fresh exact-head verifier
    participant P as Non-executing publisher
    participant M as Governed merge authority

    S-->>I: minute 07 trigger
    I->>I: select oldest eligible non-draft PR
    I->>E: exact head + live base + reviews + threads + checks
    alt current PR needs source repair and same-repository writer lease is safe
        E->>R: bounded repair task
        R->>N: NVIDIA_NIM_API_KEY only
        N-->>R: candidate patch
        R->>V: immutable bounded repair artifact
        V->>V: exact-head release/security verification
        V->>P: verified artifact identity
        P->>P: revalidate branch/ref without executing candidate code
        P-->>I: updated exact head
    else no repair required
        E-->>I: current evidence
    end
    I->>I: refetch exact head/base/reviews/threads/checks
    alt every real merge gate satisfied
        I->>M: queue expected-head squash merge
    else waiting or invalid
        I-->>S: defer affected PR only
    end
```

This diagram describes the intended accepted architecture of PR #29 but remains Proposed until that implementation merges.

## Evidence and merge state machine

```mermaid
stateDiagram-v2
    [*] --> inventory
    inventory --> needs_repair: valid current source finding
    inventory --> waiting: queued check / review latency / external gate
    inventory --> gate_clean: exact current evidence satisfies policy
    needs_repair --> verifying: bounded test-first fix
    verifying --> needs_repair: failed current-head gate
    verifying --> waiting: source clean but asynchronous gate pending
    verifying --> gate_clean: all required exact-head evidence passes
    waiting --> inventory: material state change / next sweep
    gate_clean --> merge_revalidate
    merge_revalidate --> inventory: head/base/review/check changed
    merge_revalidate --> merged: unchanged exact head + policy satisfied
    merged --> protected_main_acceptance
    protected_main_acceptance --> [*]: integrated operational evidence
```

`waiting` is not a repository-wide blocker and never authorizes a bypass.

## Authority separation

```mermaid
flowchart TB
    Model[Model reasoning] --> Proposal[Proposal / repair candidate]
    Proposal --> Verify[Deterministic verification]
    Verify --> Review[Independent review evidence]
    Review --> MergeDecision[Merge decision]
    MergeDecision --> Main[Protected main]
    Main --> ReleaseVerify[Release acceptance]
    ReleaseVerify --> Release[Versioned release]

    Model -. cannot assert .-> Verify
    Model -. cannot grant .-> Review
    Model -. cannot perform .-> MergeDecision
    Review -. does not replace .-> Verify
    Verify -. does not replace .-> Review
    MergeDecision -. does not imply .-> Release
```

No green check, LLM verdict, comment, status, or synthetic merge commit collapses these authorities into one signal.

## Failure-domain view

```mermaid
flowchart LR
    F1[Model/provider failure] --> D1[Proposal/repair action fails only]
    F2[CI/security failure] --> D2[Exact head remains unmergeable]
    F3[Reviewer latency/rate limit] --> D3[PR deferred; other work continues]
    F4[Publication credential failure] --> D4[No branch/PR mutation]
    F5[Head/base movement] --> D5[Stale write/merge refused]
    F6[Release failure] --> D6[Protected main remains; release not claimed]
```

## References

International Organization for Standardization, International Electrotechnical Commission, & Institute of Electrical and Electronics Engineers. (2022). *Software, systems and enterprise—Architecture description* (ISO/IEC/IEEE Standard No. 42010:2022). https://www.iso.org/standard/74393.html

Object Management Group. (2017). *OMG Unified Modeling Language (OMG UML), version 2.5.1*. https://www.omg.org/spec/UML/2.5.1
