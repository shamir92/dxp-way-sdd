# Technical design template (RFC)

Copy to `docs/specs/<feature>/technical-design.md`.

**RFC-shaped.** A reviewer must be able to disagree — with the approach, not
just the wording. Approved by engineering. Begins only after `ui-design.md` is approved — the
technical design is written against approved UI decisions.

The second of two design documents; the other is `ui-design.md`, owned by
the product designer and already approved. This one never restates the prototype and never redraws a
screen.

---

```markdown
# <Feature name> — technical design

Status: draft
Spec: docs/specs/<feature>/spec.md
UI: docs/specs/<feature>/ui-design.md   (omit if there is no UI surface)

## Summary

What this file currently says, in a few sentences. Update it whenever the
file changes.

## Flow (only when the feature has no UI surface)

State it here when the feature has no screen — an API-only change, a worker
job. Otherwise it lives in the UI doc and this section is deleted. Exactly
one document, never both.

| # | from | on | to | effect |
|---|------|----|----|--------|
| t1 | | | | |

## Context

What in the current system this touches, and the constraint that drives the
approach. Two to five sentences.

## Options considered

**Mandatory.** This is the subject of the approval discussion — the approver
is agreeing to a choice between alternatives, not rubber-stamping the first
idea.

| Option | How it would work | Why not chosen |
|--------|-------------------|----------------|
| Poll the provider | client polls `GET /payments/{ref}` every 2s | simpler, but no server-side recovery on timeout |
| Webhook (chosen) | provider posts to `/webhooks/payment` | requires idempotent handler and a public route |

If only one approach seems viable, the table still gets the one you would
have picked if nothing else worked, and says why it fails. "There was only
one option" is almost always a design that has not been examined — and it is
the exact claim a reviewer should challenge.

## Architecture

Where this sits in the system, and what it now couples to. Name the units
explicitly. Where units are independent with duplicated code by design —
a common choice for `backend`, `frontend`, and `worker` — a shared contract
change must name **every copy**, not just the one you edited.

| Unit | Component | Change | Why |
|------|-----------|--------|-----|
| backend | `usecase/payment.go` | new `StartTopUp` | REQ-001 |
| backend | `integration/newapi/client.go` | `CreateIntent` | REQ-002 |
| frontend | `app/(app)/wallet/topup` | new screen | AC-001.1 |

New coupling, and whether it is acceptable:

- <unit A> now depends on <unit B> for <what> — <why that is acceptable, or
  why it must be duplicated instead>

## Migrations

**The SQL, both directions.** A description is not a migration. Show the `up`
and the `down`; if the `down` loses data, say so.

```sql
-- 0005_wallet_topup.up.sql
ALTER TABLE payment_intents
  ADD COLUMN idempotency_key text NOT NULL;
CREATE UNIQUE INDEX payment_intents_idempotency_key_idx
  ON payment_intents (idempotency_key);
```

```sql
-- 0005_wallet_topup.down.sql
DROP INDEX IF EXISTS payment_intents_idempotency_key_idx;
ALTER TABLE payment_intents DROP COLUMN IF EXISTS idempotency_key;
```

Mechanism and consequence:

- Tracks: `golang-migrate` pairs under `internal/migrations/`
- **Embedded SQL needs a rebuild and redeploy**, not a config change — name
  the units that must ship for this to take effect
- Reversible? <yes / no — and if no, what is lost>
- Backfill or data migration? <what, in what order>

Delete this section only if the feature genuinely changes no schema, and say
so explicitly.

## Endpoints

**Full information at design time, not discovered during implementation.**
Omit only if the feature has no API surface. The PM states what must be true;
this document states what is observable, and the test designer derives
assertions from it.

All five, per endpoint: the list, the contract, the ordered lifecycle with
reject points, every failure code, and the `REQ` that grants access.

### Endpoint list

| Method | Path | Auth | Purpose | REQ |
|--------|------|------|---------|-----|
| POST | `/api/v1/wallet/topup` | session | start a top-up | REQ-001 |
| GET | `/api/v1/wallet/payments/{ref}` | session, owner | poll payment state | REQ-002 |

### Lifecycle — `POST /api/v1/wallet/topup`

```
auth  → validate  → usecase           → repository        → provider → response
        │            │                   │                   │
       401          400                 409 duplicate key    timeout → 202 pending
```

| Step | Where | Rejects with |
|------|-------|--------------|
| auth | middleware | `401` |
| validate | usecase (not the handler) | `400`, naming the field |
| duplicate check | usecase, before provider | `409`, returns the existing intent |
| provider call | adapter | timeout → intent stays `awaiting`, `202` |
| write | repository | `500`, captured with a sanitized summary |

Rules the lifecycle must show explicitly:

- **No DB transaction held open across an HTTP call**
- Validation lives in the usecase, never only in the handler
- Auth is checked before any write

### Contract

Request:
```json
{ "amount": 50, "method": "qris", "idempotency_key": "..." }
```

Response `201`:
```json
{ "reference": "...", "state": "awaiting_provider", "expires_at": "..." }
```

Failures — every one, not only success:

| Code | When | Body |
|------|------|------|
| `400` | amount outside allowed range | validation error naming the field |
| `409` | `idempotency_key` already used | the existing intent, no new one created |

Auth: which `REQ` grants access. State it; do not imply it.

## Acceptance mapping

Every `AC` names the design element that satisfies it, and the transition
that carries it. This is what the test designer works from.

| AC | Satisfied by | Transition |
|----|--------------|------------|
| AC-001.1 | `POST /api/v1/wallet/topup` → intent row | t1 |

**Transition ids are cited, not defined.** `t1` is defined in whichever
document owns the flow. If a transition you cite changes or disappears, this
document's approval reverts — your references are stale.

## Impact

Rollout concerns, what could break, what must be deployed in what order. Name
the units affected — a shared contract duplicated across units must name every
copy.

## Trade-offs accepted

What this design makes worse, slower, or harder. An empty section means the
design was not examined.

## Open questions

What a reviewer should challenge. **These block approval.**

| # | Question | Needs answer from |
|---|----------|-------------------|

## Testability

What the test designer needs, and what it may not invent:

- What is observable from outside: status codes, database rows, side effects
- Idempotency keys and what they are keyed by
- Concurrency points where two requests can race
- Failure-injection points: which dependency can be made to fail, and how

**Every constraint in the spec appears here as something enforceable:**

| Spec constraint | Enforced by | Observable as |
|-----------------|-------------|---------------|
| never charged twice | `409` on repeated `idempotency_key`, unique index | second request returns the original intent, one payment row |

A constraint with no row here is unimplemented, and the test designer cannot
write a `TC` for it. That is a `test design → design` fallback, not a reason
to skip the constraint.

## History

Every change to this file, newest first. Each artifact keeps its own log —
it records what changed here, not what changed elsewhere in the feature.
Excluded from the approval hash.

| Date | What changed | Approved by |
|------|--------------|-------------|
| 2026-11-02 | Initial technical design | <name> |
```

---

## Writing it

RFC-shaped means **a reviewer can disagree**, not that the document is long.
Three things earn that:

- **Options considered** — without it a reviewer can only accept or reject,
  never say "you picked polling, webhooks would be simpler"
- **Trade-offs accepted** — what this makes worse; an empty list means nobody
  looked
- **Open questions** — what should be challenged before approval

### Three sections must be concrete, not prose

| Section | Minimum | A description instead is a finding |
|---|---|---|
| **Architecture** | units touched, components, new coupling named | "extends the existing payment service" |
| **Migrations** | the `up` **and** `down` SQL, reversibility stated | "add a column to `payment_intents`" |
| **Endpoints** | the list, then each one's ordered lifecycle with reject points | a request/response example with no path |

The migration section is where hidden work tends to surface: if SQL ships as
versioned pairs and an auxiliary unit embeds it into its binary, a schema
change there requires a rebuild **and** a redeploy.
A design that shows the `ALTER TABLE` surfaces that immediately; one that
says "add a column" hides it until release.

The endpoint lifecycle is six lines and catches layering mistakes no prose
review finds:

```
auth  → validate  → usecase           → repository        → provider → response
        │            │                   │                   │
       401          400                 409 duplicate key    timeout → 202 pending
```

Validation in the handler instead of the usecase, a transaction held open
across an HTTP call, auth checked after the write — visible here, invisible
in a paragraph.

## What this document is not

**Not a plan.** No task breakdown, no ordering, no estimates. That is
`writing-plans`, and a design that sequences work becomes a second plan.

**Not the UI design.** No screens, no frame references, no prototype
inventory — those are `ui-design.md`.

**Not a restatement of the spec.** No `REQ` prose, no copied flow table.
Reference them by id.

## Before requesting approval

- [ ] Flow stated here only if the feature has no UI surface
- [ ] Architecture names every unit touched, including duplicated contracts
- [ ] Options considered names every alternative examined, each with why not chosen
- [ ] Migrations show both `up` and `down` SQL, or state that no schema changes
- [ ] Every endpoint appears in the list, with lifecycle and reject points
- [ ] Every endpoint lists its failures, not only success
- [ ] `Acceptance mapping` heading present; every `AC` appears with element and transition
- [ ] Every cited transition id exists in whichever document owns the flow
- [ ] Every spec constraint appears in the testability mapping
- [ ] Trade-offs accepted is not empty
- [ ] No open questions remain
- [ ] No task sequencing, estimates, or implementation order
- [ ] No screen or frame content — that is the other document
