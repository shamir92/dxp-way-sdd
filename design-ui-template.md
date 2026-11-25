# UI design template

Copy to `docs/specs/<feature>/ui-design.md`.

**Thin extraction, not a redraw.** The screen is the source of truth for
layout, and UI changes are made in pen.dev. This document extracts only what
the record needs — states, transitions, and the node ids that resolve — and
points at the screen. It is one of two design documents — the other is
`technical-design.md`, owned by engineering and approved separately.

Approved by the **product designer**. This is the earlier of the two design
gates: `technical-design.md` is written against this document once approved.

---

```markdown
# <Feature name> — UI design

Status: draft
Spec: docs/specs/<feature>/spec.md
Prototype: pencil:docs/<file>.pen#<frame>   |   figma:<fileKey>/<nodeId>
Read from: canvas | committed file (name which, and the date)

## Summary

What this file currently says, in a few sentences. Update it whenever the
file changes.

## Frame inventory

Every top-level frame in the file, classified. The prototype holds more than
routes — mockups, duplicated commerce screens, logo concepts — and without
this table "which frame is this route" is answered by guessing.

| frame id | name | class | route (or why not) | current? |
|---|---|---|---|---|
| `aH0SM` | Landing page | route | `/` | ✓ |
| `B9g0rw` | Group · Non-login (public) | shell-group | not a route — canvas grouping | ✓ |
| `j7U5K` | Prototype — Login gate | prototype-variant | not a route — flow mockup | ✓ |
| `Kx1Nt` | Checkout — Token subscription | commerce | not a route — out of scope here | **duplicate** |
| `Qz4Rv` | Checkout — Token subscription | commerce | not a route — out of scope here | **duplicate — which is current?** |
| `Lg09a` | Brand logo concept | brand-asset | not a screen | ✓ |
| `oi2l5` | Flow — API wallet payment | flow | not a screen — transition annotation | ✓ |

| Class | Meaning |
|---|---|
| `route` | one screen per route |
| `prototype-variant` | mid-flow mockup or alternative take |
| `commerce` | checkout screens; if a name appears twice, mark which is current |
| `brand-asset` | logos, lockups |
| `shell-group` | canvas organisation only |
| `flow` | transition annotation |
| `orphan` | fits nothing — **halt** |

Two rules this table enforces:

- **Duplicates are declared, not tolerated.** Two frames with one name and no
  "current" marker means nobody can tell which one the screen should follow.
- **A class is a claim about scope.** `commerce` frames marked out of scope
  here are in scope somewhere, or they are dead weight — say which.

## States

One row per screen the feature can show. The `checked` column is the
**pinpoint** — a reviewer opens that exact node and sees what you recorded.
"Looks right" is not a value; the observed evidence is.

The `divergence` column points at the spec's `DIV-###` row when a frame
disagrees with a decision. Mark it where a reviewer reads it; do not restate
the ruling here.

| state id | prototype node | kind | checked | divergence |
|---|---|---|---|---|
| payment.awaiting | `pencil:docs/<file>.pen#yYkYd` | state | ✓ `yYkYd` — 1440×900, text "Pay exactly [amount]", "Waiting for payment · Expires in 15:00" | — |
| payment.awaiting.failed | — | terminal | **not drawn** — proposed as `payment.failed` (draft), not approved | — |
| route.<name> | — | not drawn | — | `DIV-001` — frame is wrong, the screen stays unavailable |

The node id is the pinpoint: `yYkYd`, not "the payment screen". A reviewer
pastes it into Pencil and lands on the frame that was checked.

**A row whose frame contradicts a decision is still a row.** It records the
frame, marks the `DIV`, and says which wins — deleting the row hides that
the design and the product disagree.

## Transitions

Delete this section when the feature has **no UI surface** — the flow then
lives in `technical-design.md`. Stated in exactly one document, never
both: a duplicated flow table is two truths waiting to disagree.

| # | from | on | to | effect |
|---|------|----|----|--------|
| t1 | method.select | user confirms amount | awaiting_provider | intent created |
| t2 | awaiting_provider | provider confirms | confirmed | wallet credited |
| t3 | awaiting_provider | provider reports expiry | failed | wallet NOT credited |

## UX notes

Only what the prototype cannot convey: behaviour between screens, interaction
timing, what happens while waiting. A few lines.

## History

Every change to this file, newest first. Each artifact keeps its own log —
it records what changed here, not what changed elsewhere in the feature.
Excluded from the approval hash.

| Date | What changed | Approved by |
|------|--------------|-------------|
| 2026-11-02 | Initial UI design | <name> |
```

---

## Writing it

**Thin in prose, complete in structure.** These are the same state:

```
✗ "The payment screen displays a code with a countdown timer and
   instructions to scan with any banking app."
✓ | payment.awaiting | pencil:docs/<file>.pen#yYkYd | state |
```

The prose version becomes a third source of truth: the prototype changes,
the sentence doesn't, and now two descriptions disagree. Point at the node.

Two things must never be thin:

- **A transition the prototype shows but the spec never mentions** — that is
  `design → spec`, not permission to implement
- **A state the transition table needs but nobody drew** — write `not drawn`
  in the prototype column. Do not invent a screen

### Open the file, don't recall it

Every reference must be **resolved through MCP** — Pencil or Figma — during
this stage:

1. Open the file and list its top-level frames
2. Confirm each cited node id resolves to the frame you named
3. Screenshot each state; read its text to confirm which branch it renders
4. Record the evidence per row: node id, and what you actually saw

A citation that does not resolve is a finding, not a typo. "I verified the
design" with no resolvable reference is an unverified claim.

**And the frames must be the designer's.** The approved spec goes to pen.dev
first — the designer draws there, in their own session, and this stage picks
up the result through MCP. A canvas with no screens for this spec means the
stage has not started: stop and ask, rather than filling the states table
from the spec's flow.

### If a state is missing

A missing state is a **finding** — report it and let the designer decide.
Propose the screen only if they ask: **never modify an existing prototype
frame**. Pencil and Figma are shared, multiplayer documents; overwriting a
designer's work is destructive and unversioned. Add a new frame, mark it a
draft, and let the product designer approve or discard it. One state at a
time: a missing `payment.failed` screen is one screen to propose, not a
licence to redraw the flow.

### Prototype writes — additive only

| Action | Allowed |
|---|---|
| read, screenshot, resolve node ids | yes |
| insert a **new** frame, marked draft | yes |
| modify an **existing** frame | **never** |
| delete a frame | **never** |
| refresh stale frames to match decisions | **not this feature** — a separately scoped spec that closes its `DIV-###` rows |

Mutation on an existing frame **does not persist**. An agent that "fixes" a
frame leaves a change nobody can verify, in a file that still says the old
thing — the worst of both outcomes. Corrections live in the docs; the `.pen`
is refreshed as its own change.

### Canvas versus file on disk

**The committed `.pen` can lag the live canvas.** Observed in practice: the
app held 39 top-level nodes while the committed file held 38 — an unsaved
text node and a frame added during a session were on the canvas but not in
the file.

- **Say which one you read** in the header's `Read from:` line. Every
  `checked` cell is evidence about a specific state of the document; "the
  frame exists" is worthless if the file a reviewer opens does not contain it.
- **Reconcile before approving.** Canvas and file differing is a `DIV-###`
  row — or the file is saved first, which is the designer's action, not the
  agent's.
- An **unnamed top-level text node** is an `orphan`, not decoration. The root
  holds screens, shells, assets and annotations; anything else is a halt.

### What this document is not

**Not the technical design.** No architecture, contracts, migrations, or
options table — those are `technical-design.md`.

**Not a restatement of the spec.** No `REQ`, no `AC` prose. Reference them
by id.

## Before requesting approval

- [ ] `Read from:` names the canvas or the committed file, and the date
- [ ] Frame inventory covers every top-level frame; no `orphan`, no unnamed top-level text
- [ ] Duplicate frame names resolved — one marked current
- [ ] Canvas and committed `.pen` reconciled, or the drift is a `DIV-###` row
- [ ] Every prototype reference resolved through MCP, with per-row `checked` evidence
- [ ] Every state has a prototype node, or says `not drawn`
- [ ] Every divergence carries a `DIV-###` reference, not a restated ruling
- [ ] No existing prototype frame was modified or deleted; proposals are new and marked draft
- [ ] Transitions stated here, or the flow is deliberately in the technical doc
- [ ] No architecture, migrations, or endpoint content — that is the other document
