# Spec template

Copy to `docs/specs/<feature>/spec.md` and fill in. Delete sections
that genuinely do not apply and say why — an absent section is a question
someone will ask later.

## Before you write anything

**Scope check.** Does this request bundle several independently testable
capabilities? If yes, stop and get a capability map approved instead:

| Module id | Responsibility | Depends on |
|---|---|---|
| | | |

One spec per module, in dependency order. One module means skip this.

**Assumptions.** List what you are about to assume and ask for correction
in the same message. An assumption nobody was shown is a defect, not a
detail.

## Status values

| Value | Meaning | Effect |
|---|---|---|
| `draft` | written, not yet read by a human | design may not begin |
| `approved` | a human accepts these requirements | design may begin |
| `rejected` | the requirements are wrong — out of scope, contradictory, or describing a solution | rework the spec; design may not begin |
| `disagree` | the requirements are **as written**, but someone disputes the business decision behind them | **escalate to the requirement owner**; nothing proceeds until ruled on |

Fill in on approval: `Status: approved · <name> · 2026-11-02T14:03Z · sha256:ab12cd34`

On `rejected` or `disagree`, name the `REQ`/`AC` and the reason directly
under the status line:

```
Status: disagree · <name> · 2026-11-02T14:03Z · sha256:ab12cd34
  REQ-004 — whether a failed payment should retry automatically is a
            business decision. Currently unspecified.
```

`rejected` means the document is wrong and its author fixes it.
`disagree` means the document is right and the **decision** is contested —
the author cannot fix that, so it escalates.

---

```markdown
# <Feature name>

Status: draft
Targets: <name>/backend, <name>/frontend

<!--
Versioning: one file per feature, named after the feature — never
payment-v3.md. Add the Version line ONLY when several versions are live at
the same time (API v1 for existing customers, v2 for new ones); its
presence means "one of several live versions". A feature that simply
evolves is edited in place — history lives in git, not filenames.

  Feature: payment
  Version: api-v2
  Supersedes: payment-v1
-->

## Summary

What this file currently says, in a few sentences. Update it whenever the
file changes.

## Problem

What is wrong today, for whom, and what it costs. Two to five sentences.
If this cannot be written without proposing a solution, the problem is
not yet understood.

## Scope

**In:** what this change covers.
**Out:** what it deliberately does not, with the reason.

## Requirements

Each requirement is one behavior. If it needs "and", it is two.

| ID | Requirement |
|----|-------------|
| REQ-001 | A signed-in user can start a wallet top-up |
| REQ-002 | A top-up is not credited until the provider confirms payment |

## Acceptance criteria

Given/when/then. The `Then` must be observable from outside the system —
a response body, a database row, a side effect. "Works correctly" is not
an `AC`.

| ID | Given | When | Then |
|----|-------|------|------|
| AC-001.1 | a signed-in user with no pending top-up | they request a QRIS top-up | a payment intent exists with state `awaiting_provider`, wallet balance unchanged |
| AC-001.2 | an intent in `awaiting_provider` | the provider reports expiry | the intent is `failed`, wallet balance unchanged, reference retained |

## Flow

Every state the feature can be in, and every trigger that moves between
them. **Fallback rows are required** — if the happy path has three ways
to fail, this table has four rows.

| from | on | to | effect |
|------|----|----|--------|
| `method.select` | user confirms amount | `awaiting_provider` | intent created, wallet unchanged |
| `awaiting_provider` | provider confirms | `confirmed` | wallet credited |
| `awaiting_provider` | provider reports expiry | `failed` | wallet unchanged, reference retained |
| `failed` | user re-selects method | `method.select` | no charge |

Rules this table must satisfy:

- Every `to` is a state defined in this table (as a `from` somewhere, or
  listed explicitly as terminal)
- Every terminal state says what the user sees next
- A state with no outgoing edge is terminal — confirm that is intended

## Constraints

What must be true about the system, in business language. This is the PM's
section — state the requirement, never the mechanism.

DO:
- A user must never be charged twice for one top-up
- A payment must survive a provider timeout without losing its reference
- A user must not see another user's balance under any circumstances

DO NOT:
- `idempotency_key` is unique per request, `409` on repeat
- retry with exponential backoff, 3 attempts
- `wallet.balance` is an integer column

The mechanism belongs to the technical track; **how it is enforced, and
what the API returns because of it, is design's job.** If you cannot state
a constraint without naming a field or a status code, you are designing.

Keep only constraints this feature actually introduces. Delete the rest —
an empty section with a reason beats a filled one nobody meant.

Performance: only if this feature genuinely has a target, and give the
basis ("p99 < 2s because the QR expires visually at 15s"). A number with no
basis becomes a number people argue about later.

## Divergences

Where one artifact disagrees with another, and which wins. **A divergence
with no row is invisible, and gets rediscovered as a bug** — usually by
whoever implements the wrong one.

Authority is per fact: layout composition belongs to the prototype,
behavior to this spec, technical shape to the design. A ruling names the
owner of the fact in dispute, not the person who noticed.

| ID | Artifact A says | Artifact B says | Ruling — this wins | Owner | Date |
|----|-----------------|-----------------|--------------------|-------|------|
| DIV-001 | design: `/api-plan` is reachable | REQ-011: unavailable | **spec** — the screen keeps `notFound()` | product owner | 2026-11-01 |
| DIV-002 | design: desktop-only frames, 1999–2014 px | AC-008.1 requires a phone layout | **spec** for the requirement, **prototype** for composition — mobile is derived, no frame needed | product owner | 2026-11-01 |

Rules:

- **A ruling that changes behavior** invalidates this spec's approval; the
  spec is edited and re-approved.
- **A ruling that records layout authority** does not. It is approved with
  the divergence, because the spec never claimed the layout fact.
- Reference the ID from the design documents (`DIV-001`); do not restate the
  ruling there. One ruling, one place.
- Clearing a row means the artifact was corrected — that is a separate
  change with its own spec, not an edit made while implementing this one.

Empty is allowed only as `none found on <date>`. Absence should be a claim
someone made, not a section nobody filled in.

## Open questions

Unresolved items with who can answer them. **An open question blocks
approval** — it is a requirement with no decision behind it.

| Question | Needs answer from |
|----------|-------------------|

## Decisions

Choices made with their reason, so a later reader does not re-litigate.

| Decision | Why | Date |
|----------|-----|------|

## History

Every change to this file, newest first. Each artifact keeps its own log —
it records what changed here, not what changed elsewhere in the feature.
Excluded from the approval hash.

| Date | What changed | Approved by |
|------|--------------|-------------|
| 2026-11-02 | Initial spec | <name> |
```

---

## After writing

1. Run the self-check below
2. Ask a human to review and set `Status` to `approved`, `rejected`, or
   `disagree` with their name, date, and the commit sha they read
3. Only an `approved` status lets design begin; read the reason on any
   other value before reworking the spec

## Self-check before requesting approval

- [ ] Scope check run — one capability, or a capability map was approved first
- [ ] Assumptions were listed and none remain uncorrected
- [ ] Every `REQ` has at least one `AC`
- [ ] Every `AC` names an observable outcome, not an internal one
- [ ] Flow has a row for every failure the happy path can hit
- [ ] Every flow `to` is a defined state or declared terminal
- [ ] Every constraint is stated as a requirement, not a mechanism
- [ ] No endpoint, field name, status code, or table/column named
- [ ] No open questions remain
- [ ] Every divergence found so far has a `DIV-###` row with an owner and a date
- [ ] No row restates a ruling that belongs in another artifact
- [ ] Nothing describes an implementation choice — that is design's job
- [ ] No test cases, expected fixtures, or assertion values
