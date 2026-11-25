# Test cases template

Copy to `docs/specs/<feature>/test-cases.md`.

**Before writing a single case, read this:** you may read the spec and both
design documents — `ui-design.md` and `technical-design.md`. You may
**not** read the implementation, the diff, the plan, or the implementing
agent's report. If an expectation can only be determined from code, stop —
that is a `test design → design` fallback.

---

```markdown
# Test cases — <Feature name>

Status: draft
Spec: docs/specs/<feature>/spec.md
planTestIt: <project / suite id> — pushed on approval
Design (UI): docs/specs/<feature>/ui-design.md
Design (technical): docs/specs/<feature>/technical-design.md
Author: <agent / human>
Sources read: spec, ui design, technical design (a reviewer checks this line)

## Summary

What this file currently says, in a few sentences. Update it whenever the
file changes.

## Status values

| Value | Meaning | Routes to |
|---|---|---|
| `draft` | written, not yet read | — |
| `approved` | accepted as the acceptance criteria | implement may begin |
| `rejected` | the cases are wrong | `test design → design` or `→ spec` |
| `disagree` | the cases are right, the **behavior** is disputed | `spec` — invalidates spec approval |

Fill in on approval: `Status: approved · <name> · 2026-11-02T14:03Z · sha256:ab12cd34`

On `rejected` or `disagree`, say which `TC`s and why, directly under the
status line:

```
Status: disagree · <name> · 2026-11-02T14:03Z · sha256:ab12cd34
  TC-<feature>-006 — whether two concurrent confirmations should both be rejected
           is a product decision, not specified in AC-001.2
```

## Coverage map — requirements

This map **is** the `AC` → `TC` link. It is what makes a case traceable from
the requirement through to a run in planTestIt: `AC-001.1` → `TC-payment-001`
→ planTestIt case id → a result.

Every `AC` in the spec appears here. An `AC` with no `TC` is a gap; a `TC`
with no `AC` is invented behavior.

| AC | TC(s) | Categories covered |
|----|-------|--------------------|
| AC-001.1 | TC-<feature>-001, TC-<feature>-004 | happy, authorization |
| AC-001.2 | TC-<feature>-002 | negative, boundary |

## Coverage map — transitions

**Every row of the flow table appears here** — from the UI doc when the feature
has a screen, from the technical doc when it has none. This is a hard gate:
a transition with no `TC` blocks approval. Copy the flow table verbatim and
fill the right-hand column — do not summarize it, and do not drop rows you
find inconvenient.

| # | from | on | to | TC |
|---|------|----|----|-----|
| t1 | `method.select` | user confirms amount | `awaiting_provider` | TC-<feature>-001 |
| t2 | `awaiting_provider` | provider confirms | `confirmed` | TC-<feature>-002 |
| t3 | `awaiting_provider` | provider reports expiry | `failed` | TC-<feature>-005 |
| t4 | `failed` | user re-selects method | `method.select` | TC-<feature>-006 |

Both directions matter:

- A flow row with no `TC` → the behavior is untested. **Block.**
- A `TC` citing no transition → either a pure validation/authorization case
  (say so in its `Transition ref` field) or invented coverage

## Coverage map — levels

Every `TC` declares the level it is observed at. A level the feature can be
observed at with no case is a gap, and it is a row here saying so — not a
silent omission.

| Level | TC(s) | Harness |
|---|---|---|
| `unit` (contract-level) | TC-<feature>-001 | the automation |
| `unit` (internal) | — | implementer's own, ungated, reported in `reports/implementation.md` |
| `integration` | TC-<feature>-007 | the automation, if a harness exists |
| `system` | TC-<feature>-009 | **none — handed over to Stage 6** |
| `acceptance` | TC-<feature>-002, -005 | the automation |

Two rules:

- **`unit (contract-level)` is authored here; `unit (internal)` is not.** A
  contract-level case asserts what the design's Architecture section already
  names — given this fixture, this component returns that. A case asserting
  *how* the component does it (mocks, call counts, private helpers) cannot be
  derived from a design and belongs to the implementer.
- **`system` cases are written here and executed elsewhere.** This skill does
  not run anything against a running environment. They go to
  `reports/test-handover.md` for Stage 6.

## Scenario categories

Which of the ten apply to this feature, and which do not with the reason.

| # | Category | Applies | Covered by |
|---|----------|---------|------------|
| 1 | Happy path | yes | TC-<feature>-001 |
| 2 | Negative | yes | TC-<feature>-002 |
| 3 | Boundary | yes | TC-<feature>-003 |
| 4 | Validation | yes | TC-<feature>-002 |
| 5 | Business rules | yes | TC-<feature>-001..005 |
| 6 | Authorization | yes | TC-<feature>-004 |
| 7 | Concurrency | yes | TC-<feature>-006 |
| 8 | Integration failure | yes | TC-<feature>-007 |
| 9 | Retry and recovery | yes | TC-<feature>-008 |
| 10 | Regression risk | no — first implementation of this surface | — |

## Test cases

### TC-<feature>-001 — <scenario name, plainly>

- **AC:** AC-001.1
- **Transition:** t1 · `method.select —user confirms amount→ awaiting_provider`
- **Level:** acceptance
- **Harness:** the automation
- **Status:** approved
- **Category:** happy path
- **Preconditions:** <the exact starting state>
- **Input:** <exact values, not "valid amount">
- **Steps:**
  1. <action>
  2. <action>
- **Expected result:** <the assertion, stated as an observable fact>
- **Expected HTTP status:** `201`
- **Expected database state:** <table, columns, values>
- **Expected side effects:** <what changes outside the response>

### TC-<feature>-002 — <scenario name>

- **AC:** AC-001.2
- **Transition:** t3 · `awaiting_provider —provider reports expiry→ failed`
- **Level:** integration
- **Harness:** none — no harness for this unit; handed over
- **Status:** approved
- **Category:** negative
- **Preconditions:**
- **Input:**
- **Steps:**
- **Expected result:**
- **Expected HTTP status:**
- **Expected database state:** unchanged
- **Expected side effects:** none

## Open questions

Behavior the spec and design do not determine. **These block approval** —
they are test cases that cannot be written, and therefore requirements
that cannot be verified.

| # | Question | Spec/design gap | Needs answer from |
|---|----------|-----------------|-------------------|

## Notes for the implementer

Things a test reveals that the design should have said — missing contracts,
unnamed states, undefined error codes. Each one is a candidate
`test design → design` fallback, not something to work around.

- <observation, with the TC that surfaced it>

## History

Every change to this file, newest first. Each artifact keeps its own log —
it records what changed here, not what changed elsewhere in the feature.
Excluded from the approval hash.

| Date | What changed | Approved by |
|------|--------------|-------------|
| 2026-11-02 | Initial test cases | <name> |
```

---

## Writing a good `Expected result`

The assertion must be a fact an outside observer can check. These are
ordered from useless to verifiable:

| Bad | Why | Good |
|---|---|---|
| "payment works" | not an assertion | — |
| "wallet is updated" | which column? by how much? | `wallet.balance` increases by exactly 50 |
| "returns success" | which status? what body? | `201`, body `state: "confirmed"` |
| "error is shown" | what error? | `400`, body field `amount`, message names the range |
| "transaction is created" | — | one row in `payments` with `state='confirmed'`, `reference` matching the request |

**Test the negative space too.** For every "X happens", state what does
**not** happen — the wallet is not credited twice, no event is emitted, no
row is written. Silent side effects are what a passing suite misses.

## Handing over to execution

Execution is not part of this stage and not part of this skill. Separate
tooling runs the cases; results live in planTestIt.

What this document owes the tooling:

- Every `TC` has a `TC-<feature>-###` id — a result without one cannot be
  traced back to a case
- Every `TC` names the `AC` it verifies and the level it is observed at
- The approved cases are **pushed to planTestIt when this stage is approved**,
  not by whoever remembers later
- A `TC` that nothing automates is still pushed, and marked as needing manual
  execution — an untested case is a finding, not a gap to hide

What comes back: per-case results and a run link. Record the link; do not
copy results into this file, and never edit an approved case to match a run.

### `reports/test-handover.md`

The implement stage writes this file. It lists every approved `TC` that
could not be automated, so the external runner knows what it must pick up
and a reviewer knows what is currently unverified.

| Column | Records |
|---|---|
| `TC` | the case id |
| Level | `unit` / `integration` / `system` / `acceptance` |
| Why not implemented | no harness, needs a deployed environment, needs a provider, out of this unit's scope |
| Unblocked by | the harness, environment, or feature that would make it automatable |

A case in that file is **unverified, not passed**. `system`-level cases
always land there, because this skill never runs anything against a running
environment.

## Self-check before requesting approval

- [ ] Every `AC` appears in the coverage map with at least one `TC`
- [ ] **Every row of the design's flow table appears in the transition map with a `TC`**
- [ ] **Every `TC` declares a level, and every level the feature can be observed at has a `TC` or a coverage-map row saying why not**
- [ ] Every `TC` names a transition, or states why it has none
- [ ] `TC` ids are globally unique — `TC-<feature>-###`, not `TC-001`
- [ ] Every `TC` carries its own `Status`
- [ ] No `TC` exists without an `AC` reference
- [ ] All ten categories marked applies/not-applies, with reasons for skips
- [ ] Every expected result is observable from outside the system
- [ ] Every state-changing `TC` says what the database looks like after
- [ ] Every `TC` says what does **not** happen as well as what does
- [ ] Failure branches from the design's flow table each have a `TC`
- [ ] No `TC` was derived from reading the implementation
- [ ] No **contract-level unit** `TC` asserts internal structure — mocks, call counts, private helpers belong to the implementer
- [ ] Every `system`-level `TC` is marked for handover, not for local execution
- [ ] Open questions are listed, not resolved by guessing
- [ ] `Sources read` names only the spec and the two design documents
- [ ] Every `TC` id is globally unique and carries the feature prefix
- [ ] Coverage map links every `AC` to at least one `TC`
- [ ] `planTestIt:` names where the cases will be pushed
