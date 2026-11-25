---
name: spec-driven-development
description: Use when starting any feature, change, or bugfix that needs a spec before code. Governs the spec -> design -> implement pipeline with human approval gates and backward fallback. Invoke before brainstorming, before writing plans, and whenever work must be traced back to an approved requirement.
---

# Specification-Driven Development

A pipeline with approval gates and governed backward edges. Work moves
forward only through an approved artifact; when a later stage finds an
earlier one wrong or incomplete, it routes backward — never sideways.

```
spec ──► ui-design ──► technical-design ──► test-cases ──► implement ──► [external verification]
  ▲           ▲                ▲                 ▲              │
  │           │                │                 │              │
  └─ behavior ┴─ screen/UI ────┴─ technical ─────┴── cases ─────┘
     wrong       wrong            approach          incomplete
                                  wrong
```

Sequential. Each gate opens only on the previous artifact's approval. When a
later stage finds an earlier artifact wrong, work returns to the **earliest**
artifact that needs correcting — not to the one nearest the discovery.

**Spec approval is not a handoff into UI design.** `spec → ui-design` is a
**handoff point held by the human**, not a gate that opens on its own: the
designer reads the approved spec and draws in the design tool (pen.dev),
outside this session, and the UI stage begins only when that work comes back
through MCP. So after approving a spec, **stop and ask** whether to continue —
see Stage 1, *After the spec is approved*.

## When to use

Use for any work that will be read by someone other than its author, or
that must be traceable after the fact. Skip for spikes and throwaway
probes — `brainstorming` classifies those, and this skill applies to its
**bounded** and **architectural** paths, not to **spike**.

This skill does not replace `brainstorming`. Brainstorming decides *what*
to build; this skill records *what was agreed* and controls what may be
built from it. A bounded task whose design fits in a chat message still
gets a spec entry — it is one table row, not a document.

## The stages

### Stage 0 — scope check

Most requests describe one capability. If this one does, skip this stage
and go straight to spec. It exists for the exception.

**Decompose first** when a single request bundles several independently
testable capabilities:

- It names distinct capabilities with their own consumers or data
  (identity, billing, notifications, reporting)
- Acceptance criteria cluster into groups that could ship and be
  verified separately
- One capability could be cut or replaced without rewriting the others

When that is true, write a **capability map** in chat and get it approved
before writing any spec:

| Module id | Responsibility | Depends on |
|---|---|---|
| identity | Accounts, sessions, SSO | — |
| billing | Plans, invoices, payments | identity |

Rules:

- **Stable ids**, kebab-case, chosen once. Specs and tasks select work by
  id instead of guessing which spec is active.
- **No dependency cycles.** If two modules each need the other, they are
  one module.
- **Interfaces live at the boundary** — the contract belongs in the
  provider module's spec, not duplicated in both.

Then run spec → design → implement **per module, in dependency order**.
A map that is wrong is expensive; reviewing ten lines is not.

Decomposition is not a planning detail. Planning slices *within* a spec;
by then the oversized artifact already exists and every downstream task
must reason over the whole contract.

### Stage 1 — spec

The requirement. Produced by a human decision, written to
`docs/specs/<feature>/spec.md` from `spec-template.md`.

**Before writing the spec, state your assumptions.** List every guess you
are about to make and stop for correction:

```
ASSUMPTIONS I'M MAKING:
1. Auth is session cookies, not JWT
2. One wallet per user, not per organization
3. Balances are integer credits, never floats
→ Correct me now or I'll proceed with these.
```

An unexamined assumption is the most expensive kind of misunderstanding,
because it survives review: the spec is approved, the code is built, and
the wrong premise was never a sentence anyone could object to.

Required sections:

- **Status** — approval block (see below)
- **Summary** — what this file currently says, in a few sentences
- **Targets** — one or more `<name>/<unit>` paths
- **Requirements** — `REQ-###`, one behavior each
- **Acceptance** — `AC-###.#`, given/when/then, observable
- **Flow** — state/transition table including every fallback branch
- **Constraints** — what must be true, in business language
- **History** — date, what changed, who approved (see Artifact storage)

**Not in the spec: test cases.** Test design is a separate stage performed
by someone who did not write the spec. Putting expected outcomes in the
spec collapses expectation and implementation into one author — the exact
failure this skill exists to prevent.

**Not in the spec: endpoints, fields, or mechanisms.** The spec states
what must be true — *"a user must never be charged twice"*. Design states
what is observable and how it's enforced — `409` on a repeated
`idempotency_key`, a unique index. Three questions, three artifacts, one
owner each:

| Question | Owner | Artifact |
|---|---|---|
| What must be true? | PM | spec → `Constraints` |
| What is observable? | engineering | design → endpoints, contracts |
| How do we verify it? | test designer | test cases |

A PM naming a status code is approving a contract they cannot evaluate,
and design then inherits a decision it never made. This is why test design
runs after design: the observable surface exists there, so the spec does
not need to guess at it.

#### After the spec is approved — pause, do not proceed

**An approved spec does not advance into `ui-design` in the same turn, or
on its own.** The spec is the input to design work the agent does not do:
the product designer reads this spec and draws the screens in pen.dev,
under their own session. UI design begins when that work comes back through
MCP and shows up on the canvas — not when the spec's status line says
`approved`.

So the end of Stage 1 is a question, not a transition:

```
Spec approved · docs/specs/<feature>/spec.md · <REQ/AC count>
Next stage is UI design, and it starts from screens drawn in pen.dev —
not from this document. Do you want to continue to ui-design now,
or take the spec to pen.dev first and come back?
```

- **Continue means "begin by opening the prototype"**, not "write
  `ui-design.md` from the spec." If the designer has not drawn the screens
  yet, there is nothing to extract, and every row of the states table would
  be a guess — see Stage 2, *go to the design tool, don't recall it*.
- **Stop means stop.** No `ui-design.md` skeleton, no frame inventory
  guessed from the spec's flow table, no list of screens you expect the
  designer to produce. That document is extracted from what exists on the
  canvas, and a skeleton written before the canvas has screens is
  invention.
- **Ask once, at the approval.** Not every turn after it.

This is the same rule as "the approval request ends your turn" applied one
step further: the human who approves the spec is the one who decides when
the designer's work becomes the next input.

#### Stage 2's handoff — receive the design, don't redraw it

The designer's output arrives as `.pen` frames reachable through MCP. The
UI stage's job is to **receive that state and record it**, not to produce a
design of its own: read the frames the designer made, resolve the node ids,
write the extraction. See Stage 2.

### Stage 2 — ui-design

The first of two design documents, and the earlier gate. It is approved
before the technical design is written; the technical design is authored
against an *approved* UI document, then approved on its own.

**Thin extraction, not a redraw.** The screen is the source of truth for
layout, and UI changes are made in pen.dev. `ui-design.md` extracts only what
the record needs — states, transitions, and the node ids that resolve — and
points at the screen. It does not describe what the screen looks like; the
prototype is the description.

| Order | Document | Owner | Template |
|---|---|---|---|
| 1 | `docs/specs/<feature>/ui-design.md` | product designer | `design-ui-template.md` |
| 2 | `docs/specs/<feature>/technical-design.md` | engineering | `design-technical-template.md` |

Sequencing is not ceremony. The technical design is written against UI
decisions, and if both are authored at once, one of them guesses about the
other. Approving UI first makes the dependency real instead of something a
reviewer has to notice.

`<feature>-design.md` is the legacy single-file form. It stays valid where
it already exists; split it into the two documents next time it is edited.

**The flow table is stated in exactly one document** — the UI doc when the
feature has a screen, the technical doc when it has none. Not both: a
duplicated flow table is two truths waiting to disagree.

**Cross-document citation is the coupling.** The technical doc cites
transition ids (`t3`) in its acceptance mapping but never defines them. If
the UI doc later changes a transition it cites, the technical approval
reverts — its references are stale. A change to an uncited transition
leaves it standing.

**UI document — go to the design tool, don't recall it.** The prototype lives
outside this repository. The agent must **open it through MCP** (Pencil
`.pen`, or Figma) and work against what is actually there — never against
a description of it.

**And it works against what the designer drew there, not a design of its
own.** This stage runs *after* the designer has taken the approved spec to
pen.dev and produced the screens; the agent's input is that canvas. A stage
that finds the canvas unchanged since the spec was approved is not in the UI
stage yet — it is waiting, and it asks rather than proceeding.

Two modes, and they are not interchangeable:

| Mode | When | Permission |
|---|---|---|
| **Verify** | the designer's screens exist on the canvas | read-only |
| **Design** | no prototype exists for a required state — the designer asked for a proposal | **write, as a draft** |

**Verify** is the normal path and means resolve every reference and prove it
exists:

- Open the file, list the top-level frames, confirm each referenced node id
  resolves to the frame you claim
- Screenshot each state; read its text content to confirm the branch it
  renders
- Walk the transitions and confirm each `to` has a real screen
- Record the evidence: node id + what you saw, per row

A row whose node id does not resolve, or whose screenshot shows a different
state than claimed, is a finding — not a formatting problem.

**Design** means the state is missing and you propose it — but:

- **Only when asked.** A missing state is a finding and a `ui-design → spec`
  route by default; proposing it is something the designer requests, not
  something the agent does on its way to a complete `ui-design.md`. The
  designer owns the canvas, so they decide whether the gap closes here or in
  their own pen.dev session.
- **Never modify an existing prototype.** Pencil and Figma are shared,
  multiplayer documents; overwriting a designer's work is destructive and
  unversioned. Add new frames; do not edit theirs.
- **Mark it a draft** — the product designer approves it like any other
  artifact, or discards it.
- **One state at a time.** A missing `payment.failed` screen is a state to
  propose, not a licence to redraw the flow.

Rules that hold in both modes:

- Every screen is referenced by `pencil:<path>#<frame>` or
  `figma:<fileKey>/<nodeId>`, and the reference must resolve
- Every transition between screens — trigger, effect
- Every failure branch the prototype renders

**The states table carries the pinpoint.** Each row records the node id that
resolved and what was observed there, so a reviewer can open that exact
frame and check the claim. `yYkYd`, not "the QRIS screen". A row with no
resolvable node id is unverified.

A transition the prototype shows but the spec never mentions is a
**divergence**, not permission to implement it. It becomes a `DIV-###`
ruling — behavior is the spec's fact, so this one routes to
`ui-design → spec` and withdraws approval. See Truth and authority.

A screen the transition table needs but no prototype shows is a
**`ui-design → spec` fallback** too — the requirement is real, the design
isn't finished. Do not implement a state nobody drew and nobody specified.
Propose the screen, or route back.

**"I verified the design" is not evidence.** The design doc carries, per
row, the node id that resolved and what was observed there. A verification
claim with no resolvable reference is an unverified claim.

### Stage 3 — technical-design

Written against the *approved* UI document, then approved on its own.

**The flow table is stated in exactly one document** — here when the
feature has no UI surface (an API-only change, a worker job), the UI doc
when it has a screen. Never both: a duplicated flow table is two truths
waiting to disagree.

**Technical document — RFC-shaped.** For each `REQ`, how it will be satisfied.
These sections carry the weight, because they are what lets a reviewer
disagree before code exists (`design-technical-template.md` also carries Context, Acceptance
mapping and Testability alongside them):

| Section | Without it |
|---|---|
| **Architecture** | nobody can tell where this sits in the system, or what it now couples to |
| **Migrations** — actual SQL | the schema change is discovered during implementation, and reversibility never examined |
| **Endpoints** — list, lifecycle, contract, failures, auth | the request path is invented while coding; auth and validation land in the wrong layer |
| **Options considered** — mandatory | a reviewer can only accept or reject, never say "webhooks would be simpler" |
| **Acceptance mapping** — a required heading: `AC` → element → transition | the test designer cannot tell which behavior each test case is asserting |
| **Impact** | rollout order gets discovered during implementation |
| **Trade-offs accepted** | the design was not examined, only chosen |
| **Open questions** | the document pretends to be finished when it isn't |

Three of those are prose-free and must be concrete:

**Architecture.** Where this sits: which units are touched, which components
inside them, and what new coupling it creates. Where units are independent
with duplicated code by design — a common choice for `backend/`, `frontend/`,
and `worker/` — a shared-contract change must name **every copy**. A drawing or a short component list, not a paragraph of
prose.

**Migrations — the SQL, not a description.** Both directions, written out:
the `up` that changes the schema and the `down` that reverses it. A design
that says "add a column to `external_site_accounts`" has not been designed;
one that shows the `ALTER TABLE` and its `DROP COLUMN` has. Two things this
forces into the open:

- Irreversibility — a `down` that loses data must say so
- Where the SQL lands — here, `golang-migrate` pairs under
  `internal/migrations/`; the worker embeds SQL via `go:embed`, so a schema
  change there means a rebuild **and** a redeploy, not a config change

**Endpoints — full information at design time.** All five, per endpoint:
the list, the request/response contract, the ordered lifecycle with reject
points, every failure code and when it fires, and which `REQ` grants access.
Anything less is discovered during implementation, which is where auth and
validation land in the wrong layer.

```
POST /api/v1/wallet/topup
  auth → validate → usecase → repository → provider → response
  401 at auth · 400 at validate · 409 at usecase (duplicate key)
  no transaction held across the provider call
```

The lifecycle is where layering mistakes become visible — validation in the
handler instead of the usecase, a DB transaction open across an HTTP call,
auth checked after the write. Those are reviewable in six lines and
invisible in a paragraph.

**Options considered is mandatory and is the subject of the approval
discussion.** The approver is agreeing to a choice between alternatives, not
rubber-stamping the first idea. If only one approach seems viable, write the
one you would have picked if nothing else worked and say why it fails —
"there was only one option" is almost always a design that has not been
examined, and it is precisely the claim a reviewer should challenge.

RFC shape applies to **the writing, not the process**: present options,
state open questions, get approval once. An approval that invites a second
round of redesign is not an approval.

Design may add detail. It may not change behavior, drop an `AC`, or
introduce a dependency no spec constraint requires.

**The technical document is not a plan.** No task breakdown, no ordering, no
estimates — that is `writing-plans`, and a design that sequences work
becomes a second plan saying "do this in this order."

The two documents must agree. A flow transition with no technical handling,
or a component with no transition that reaches it, is an unresolved
conflict — fix it inside design, don't carry it forward.

Testability inputs — not test cases — belong in this stage:

- Each `AC` mapped to the transition or contract that satisfies it
- Idempotency keys, concurrency points, and failure-injection points named
- What is observable from outside: status codes, database rows, side effects

### Stage 4 — test design

Written to `docs/specs/<feature>/test-cases.md`. Begins only after the
technical design is approved. Consumes the spec's `AC` and the design
documents' flow and contracts; **never reads the implementation.**

The ordering enforces that: implementation has not started, so there is no
code to read. That is stronger than a rule the author could break — the
`Sources read:` line makes it auditable when the ordering is violated.

Test design is done by an **agent, approved by a human**. That works only
under one rule:

> The test-design agent may read the spec and the design. It may not read
> the implementation, the diff, the plan, or the implementing agent's
> report.

Reading the code corrupts the test: you get assertions describing what was
built rather than what was required, and the suite goes green on wrong
behavior. If test design cannot be done without reading code, that is a
**`implement → design` fallback** — the design is under-specified.

**Three coverage axes, all mandatory.**

| Axis | Unit | Source | Rule |
|---|---|---|---|
| Requirements | `AC-###` | spec | every `AC` has at least one `TC` |
| **Transitions** | one row of the flow table | design | **every transition has at least one `TC`** |
| **Levels** | `unit` / `integration` / `system` / `acceptance` | design | **every level the feature can be observed at has at least one `TC`** |

Transition coverage is a **hard gate, not a metric.** A transition is a
trigger plus an effect — exactly what a `TC` asserts — so an untested
transition is an unverified behavior, however many `AC`s are green.

An edge with no `TC` is a gap. A `TC` that traverses no edge is invented
behavior, unless it is a pure validation or authorization case with no
state change.

Why this axis matters more than `AC` coverage: `AC`s are written by the
spec author, so a branch the spec author forgot is invisible to the `AC`
axis and covered-looking. The flow table is written in design, where the
branch had to be drawn to exist at all. **The flow table is the
completeness check on the acceptance criteria.**

Consequence to accept: some transitions cannot be tested in isolation —
`provider confirms → confirmed` needs the provider. Those become
integration `TC`s with a controlled dependency. If the unit has no harness
for them, the case is **unverified, not skipped**: it is recorded in the
coverage map and handed over in `reports/test-handover.md`.

### Test levels

Every `TC` declares the level it is verified at. The level is a property of
the case, not a separate document — a feature does not get "a unit test
file" and "an acceptance test file", it gets cases that each name their
level.

| Level | Observes | Derivable from | Executed by |
|---|---|---|---|
| `acceptance` | the `AC`'s stated outcome | spec | the automation, or external tooling |
| `system` | the feature end to end, against a running environment | flow transitions, contracts | **external tooling only** — Stage 6 |
| `integration` | the unit against a real or controlled dependency | design's failure-injection points | the automation, if a harness exists |
| `unit` | one component's contract | design's component contracts | the automation |

**Unit cases split in two, and the split is what preserves independence.**

| | Authored by | Gated | Reads the implementation |
|---|---|---|---|
| **unit (contract-level)** | test design | yes | no — derived from the design's component contracts |
| **unit (internal)** | implementer | no, but **reported** | yes — mocks, private helpers, edge cases |

A contract-level unit `TC` asserts what the design already names: given a
fixture, `UserRepo.GetByEmail` returns the user for a known email. That
needs no code reading, so it stays inside the test designer's read
restriction. A unit test asserting *how* the component does it — call
counts, mock expectations, private helpers — cannot be derived from a
design, and belongs to the implementer, ungated.

The gate on contract-level unit cases exists so that unit coverage is
**auditable**. The freedom on internal unit tests exists so the implementer
is not gated on its own implementation strategy. Both are implemented by
the same agent; the difference is who authored the case and whether a human
approved it.

**A level with no `TC` is a gap, and it is recorded — not skipped.** If a
feature can be observed at a level and no case covers it, that is a row in
the coverage map saying so. If a case exists but the unit has no harness to
execute it, the case is **unverified**, and it is handed over in
`reports/test-handover.md` — see Stage 5.

Each test case records:

| Field | Purpose |
|---|---|
| `TC-<feature>-###` | stable, globally unique id — referenced by implementation and QA |
| `AC` ref | which acceptance criterion it verifies |
| Transition ref | which flow row it exercises — `from → on → to` |
| **Level** | `unit` / `integration` / `system` / `acceptance` — where it is observed |
| **Harness** | the runner that executes it, or `none` — a `none` is a handover, not a pass |
| Scenario | one behavior, named plainly |
| Preconditions | state before the test |
| Input | exact values |
| Steps | what is done |
| Expected result | the assertion |
| Expected HTTP status | if there is an API surface |
| Expected database state | if state changes |
| Expected side effects | credit applied, event emitted, nothing otherwise |

Required scenario categories — every feature covers all that apply:

1. Happy path
2. Negative (invalid input, wrong auth, missing permission)
3. Boundary (zero, max, off-by-one, empty)
4. Validation (rejected vs. accepted, and what the error says)
5. Business rules (each `AC` has at least one)
6. Authorization (a user cannot act on another user's resource)
7. Concurrency (two identical requests, one wins)
8. Integration failure (dependency down, timeout, malformed response)
9. Retry and recovery (safe to repeat, keyed by what)
10. Regression risk (what could this break that tests don't cover)

**Test cases may not be edited to make an implementation pass.** A failing
`TC` means the implementation is wrong, or the `TC` is wrong — and if the
`TC` is wrong, the correction is re-approved by a human like any other.

**Ambiguity is reported, not resolved.** A test designer that cannot
determine expected behavior from the spec and design records an open
question. It does not invent a plausible answer.

### Test case identity

`TC` ids are **globally unique**, not per file: `TC-<feature>-001`, e.g.
`TC-payment-004`. Per-file ids collide the moment a second file exists, and
retrofitting a prefix across hundreds of cases is a migration nobody does.

Also fixed at authoring time:

- **Status is per `TC`.** The file-level `Status:` describes the set; an
  individual case carries its own, so one disputed case does not block
  forty approved ones.
- **Every automation is named after its `TC`** — `TestTC_payment_004`, or a
  `// TC-payment-004` comment where a name would be unwieldy. This is what
  lets a script answer "is this case automated?" without reading prose.

### Execution is a separate skill

This skill defines **what must exist and who approves it**. It does not run
anything.

Running the cases, collecting evidence, seeding fixtures, and reporting
pass/fail belong to a separate test-runner skill. The contract between them:

- The runner **reads** the approved test-case file
- The runner **writes a separate evidence report** — results are never
  written back into the approved test-case file, because editing a
  approved artifact silently invalidates its approval — the body hash no
  longer matches the revision named in its status line
- The runner reports per-`TC` results keyed by the ids above

Keeping them apart means a broken runner cannot invalidate an approved
spec, and a rejected `TC` cannot block a test run.

### Test case status

Test cases use the same four values as every gated artifact. What is
specific to this stage is where each failure state routes:

| Status | Routes to |
|---|---|
| `rejected` — the cases are wrong (invented scenarios, expectations that don't follow from spec or design) | `test design → design`, or `→ spec` if the trace itself is bad |
| `disagree` — the cases are right, the behavior is disputed | **`spec`** — and this invalidates the spec approval |

`rejected` blames the test author. `disagree` blames the requirement.
They need different people, different files, and different follow-up.

Implementation begins only when all four status values above resolve to
`approved`.

### Stage 5 — implement

Code written to the approved technical design, satisfying the approved test
cases. **This stage's exit condition is "code merged, the implementer's own
tests pass, a deployable candidate exists" — not "verified."** Verification
runs on a deployed environment, in the next stage.

Four deliverables, and they are not interchangeable:

| Deliverable | Source | Gated |
|---|---|---|
| **`TC` automations** — contract-level unit, integration, acceptance | the approved test cases, one per `TC-<feature>-###` | yes, by test design approval |
| **Internal unit tests** | the implementer's own judgment — mocks, private helpers, edge cases | no, but **reported** in `reports/implementation.md` |
| **`reports/test-handover.md`** | every approved `TC` this stage could not implement | yes, before claiming completion |
| **Evidence** | the command run and its output | yes, before claiming completion |

Both unit kinds are implemented by the implementer. The difference is
authorship and gating, not who writes the code: contract-level cases come
from the approved test design, internal ones from the implementer's own
judgment. Internal unit tests are ungated but **not invisible** — the
implementation report states what they cover, so a reviewer can see whether
the implementer wrote any at all.

Rules:

- Write tests before or alongside code; never after, to match what was written
- Do not weaken an approved expectation to make an implementation pass
- Do not silently change an approved requirement — route backward instead
- Follow the repository's existing conventions and architecture
- Every approved `TC` maps to **exactly one** automation, named by its id
- Every flow transition has an automation — the coverage map has no empty row

**The `TC` automation must fail before the feature exists.** Automate the
`TC`, run it, watch it fail for the right reason, then implement. If a
`TC` cannot be made to fail, it is not testing the behavior — either the
behavior already existed (re-check the `TC`), or the automation is
vacuous. `git stash` the implementation to prove it if needed.

This is not optional ceremony. An implementer who automates the `TC`s
decides whether the automation is faithful, and an assertion written to
pass will pass. The RED step is the only cheap check that the automation
is connected to the behavior rather than to the implementation.

**Report executed evidence, never conclusions.** The completion claim is
the command and its output, not "tests pass." A stage whose evidence is a
sentence is a stage nobody verified.

Implementation strategy is free. Rules, task order, and file decomposition
are the implementer's choice.

**If a unit has no test runner, record it as a finding — not a halt.** A
`TC` that cannot be automated because the unit has no harness is unverified,
not passed. Record it and let it travel with the feature; do not work around
it by leaving the `TC` unautomated, and do not stop the stage on it.

### `reports/test-handover.md` — what this stage could not implement

Every approved `TC` the implementer did not automate is listed here, with
the reason and what would unblock it. This is the bridge to Stage 6: the
external runner reads it to know which cases it must pick up, and a reviewer
reads it to know which approved requirements are currently unverified.

| Column | Records |
|---|---|
| `TC` | the case id |
| Level | `unit` / `integration` / `system` / `acceptance` |
| Why not implemented | no harness, needs a deployed environment, needs a provider, out of this unit's scope |
| Unblocked by | the harness, environment, or feature that would make it automatable |

Two rules:

- **A case in this file is unverified, not passed.** The handover is a
  finding with a home, not a way to close a row.
- **`system`-level cases always land here.** This skill does not run
  anything against a running environment; that is Stage 6, external. The
  test design writes them, the implementer cannot execute them, and the
  handover is where they wait.

The task list that drives this stage is a **briefing, not an artifact** —
see Artifact types.

### Stage 6 — verification (external)

**This skill does not run verification.** Apart from the implementer's own
unit tests, execution is done by separate tooling against a running
environment, and the results live there.

This skill's obligations end at handing over an approved, addressable set of
cases:

1. Every `TC` is linked to the `AC` it verifies — the coverage map is that
   link, and an `AC` with no `TC` is a gap
2. Every `TC` carries its `TC-<feature>-###` id and its level
3. The approved cases are **pushed to planTestIt as part of this stage**,
   not as a follow-up someone remembers later
4. `reports/test-handover.md` lists every approved `TC` the implement stage
   could not automate, with the reason and what would unblock it — the
   external runner works from this file for the cases it must pick up

What comes back from the tool is evidence, not a gate this skill enforces:

| Returned | Recorded |
|---|---|
| per-`TC` results for a revision | planTestIt |
| the run reference | linked from the feature, so "it passed" points at something openable |
| cases with no automation | a finding — an approved case that nothing executes is unverified, however green the board looks |

**A `TC` result keyed to nothing is not a result.** If a case cannot be
traced from the spec's `AC` to a `TC` id to a run in planTestIt, the chain is
broken at whichever link is missing — and a missing link is a finding, not a
pass.

The mechanics — what runs the cases, which environment, how a revision is
pinned — belong to the tooling and to whoever operates it. Do not build that
here, and do not describe it as done.

## Artifact storage

**One current set of artifacts per feature.** Not one file per change — that
makes approval churn, and not one file per version — that multiplies the
documents. A feature owns a folder.

In a repository:

```
docs/specs/repayment/
├── spec.md
├── ui-design.md
├── technical-design.md
├── test-cases.md
├── tech-debt.md
├── reports/
│   ├── implementation.md
│   ├── test-handover.md
│   └── verification.md
├── design-evidence/
└── plan.md            ← optional, ungated, regenerable
```

In Outline: a collection per product area, a parent document per feature,
and the artifacts as child documents — same structure, same names.

| Artifact | Records |
|---|---|
| **spec.md** | product intent, behavior, requirements, acceptance criteria, flow, business constraints, divergences |
| **ui-design.md** | approved screen states, layout, interactions, references to the design tool |
| **technical-design.md** | architecture, contracts, schema, migrations, approach, trade-offs |
| **test-cases.md** | how each approved acceptance criterion and flow will be verified |
| **tech-debt.md** | what was knowingly deferred, why, and what would bring it back |
| **reports/implementation.md** | what changed, deviations from the design, commands run, and what the internal unit tests cover |
| **reports/test-handover.md** | every approved `TC` the implement stage could not automate, why, and what would unblock it — the external runner's worklist |
| **reports/verification.md** | the link to the planTestIt run and who verified it — results stay in the tool |
| **design-evidence/** | captures and other evidence for a design with no reliable version history |

### Summary and History — in every artifact

Every artifact — `spec.md`, `ui-design.md`, `technical-design.md`,
`test-cases.md`, `tech-debt.md`, and the files under `reports/` — opens with
a `## Summary` and closes with a `## History`.

Reports are not gated, but they are still artifacts: a reader opening
`reports/implementation.md` alone should see what the feature did and when,
without going to look for the spec. The `Status:` line is what reports do
not carry — not the Summary and History.

- **Summary** — what this file currently says, in a few sentences. It is the
  first thing a reader sees, and it is updated whenever the file changes.
- **History** — this file's own change log, newest first:
  `| Date | What changed | Approved by |`. Each artifact keeps its own log:
  it records what changed **here**, not what changed elsewhere in the
  feature. A spec change appears in the spec's history, not in the
  `ui-design.md` history.
- **The History section is excluded from the approval hash.** It is a log,
  not content; updating it must not invalidate an approval. The hash covers
  the body minus the status line and minus `## History`.

**Debt is per feature, in the feature folder.** It does not live inside the
spec, because the spec is revision-validated: paying off debt would otherwise
force re-approval of requirements that did not change. Each entry records the
debt, why it was accepted, and the trigger that makes it urgent — a deferred
item with no trigger is a forgotten one.

Debt is not the same as a divergence. **Debt is deferred work**; a `DIV-###`
in the spec is a decided disagreement between two artifacts. Different
lifecycles, so different homes — both feature-scoped.

**The plan is a working aid, not an artifact.** No `Status:` block, no gate,
regenerable at will (`writing-plans` owns its format). A plan that
contradicts the design is wrong by definition; a plan that cannot be written
without deciding something the design does not cover is a design gap.

**The design documents are gated, the prototype is not.** Pencil and Figma
files live outside the repository and cannot be hashed against an approval,
so the prototype is **referenced by ID** and `ui-design.md` is the artifact
that carries approval. `design-evidence/` exists for exactly this reason:
when the design tool has no reliable version history, a committed capture is
the durable evidence.

**Legacy layout.** Flat, date-prefixed artifacts (`docs/specs/2026-11-01-<feature>.md`)
stay valid where they exist. Migrate a feature to its folder the next time
it is edited; do not migrate them in a batch as an unrelated change.

## Truth and authority

There is no single authoritative document. Authority is **per fact**, and
which artifact wins depends on what kind of fact is in dispute — never on
which file was edited last.

| Fact kind | Authority | Cannot be overridden by |
|---|---|---|
| business intent, behavior, scope | **spec** (approved) | a prototype frame |
| layout composition — what appears, in what order, at what emphasis | **prototype** (designer) | spec prose |
| technical shape — contracts, schema, layering | **technical design doc** | prototype |
| what exists today | **code** | any document |
| how a disagreement was settled | **the spec's `DIV-###` ledger** | nothing implicit |

Rules:

- **Disagreement is not automatically a fallback.** Find which fact kind is
  in dispute, then ask who owns that kind. A stale frame is the designer's
  fact; a missing requirement is the PM's. Routing everything to the spec
  asks a PM to re-approve a document to fix something that was never
  business-owned.
- **A ruling is recorded before work continues** — `DIV-###` in the spec,
  marked inline in the design doc. A divergence with no row is invisible
  and gets rediscovered as a bug.
- **A ruling that changes behavior** still invalidates spec approval. A
  ruling that records **layout authority** — mobile derived because the
  frames are desktop-only, a frame stale against a later decision — is
  approved with the divergence and does not reopen the spec.
- **Neither artifact is rewritten to match the other when it cannot be.**
  The prototype does not persist mutation on existing frames; the spec is
  sha-locked. The ruling is the durable artifact, and refreshing the
  prototype is a separate feature with its own `DIV-###` closure.
- The design doc **references** `DIV-###`; it never restates the ruling.
  One ruling, one place, or the two copies drift.

## The artifact is the durable record

The spec, the design documents, and `tech-debt.md` are the project's
**portable** record — they live in version control and travel between
machines and sessions. Local memory does not: it is per-machine, it drifts,
and it is never authority.

- **Anything durable goes into the artifact.** A decision, a divergence, a
  deferred item, an open question — if the next session needs it, it belongs
  in `spec.md` (`DIV-###`, open questions), `tech-debt.md`, or the design
  docs. Not in memory.
- **Memory is a local cache, never a source.** A fact that exists only in
  memory is not part of the project's record; it will be lost on another
  machine. Treat it as a hint to verify, not as truth.
- **Keep the spec current by editing it in place and re-approving.** The
  edited revision becomes `draft`; the previous approval is history. A stale
  spec on a fresh laptop is worse than a long one.

The cost: a spec that carries every decision is longer and needs re-approval
more often. That is the price of portability, and it is the right one.

## Updating an existing feature

**A feature's spec describes its latest approved behavior.** For an evolution
of the same feature, update its current spec — do not create a new numbered
spec.

That is the whole rule, and it follows from the storage model: one artifact
set per feature, edited as the feature evolves.

```markdown
docs/specs/repayment/spec.md     ← updated in place, approved again
```

The edited revision becomes `draft` and needs re-approval; the previously
approved revision is the baseline, preserved as history. See Approval.

### When the old and new behavior coexist

Adding a refund path to repayment is an evolution: edit the spec.

Running **API v1 for existing customers and v2 for new ones** is not. Both
behaviors must be true at once, so they are two features:

```
docs/specs/repayment-v1/spec.md
docs/specs/repayment-v2/spec.md
```

The test: *can the old and the new be true at the same time?* No → edit the
current spec. Yes → two features, each with its own artifact set.

**Naming.** A feature folder is named after the feature. A `Version:` line
appears in the spec only when versions coexist, because its presence means
"one of several live versions" — which a folder name cannot express
unambiguously. Never mix a bare name with versioned siblings: `repayment/`
next to `repayment-v2/` reads as v1 to nobody.

**Retiring a version.** When a version is superseded and no longer live,
delete its folder. Version control preserves it; the repository should show
what is current. Keeping superseded folders "for reference" means months
later nobody knows which one is authoritative, and both get edited
imperfectly.

## Trivial changes — the lightweight path

Not every change needs the full pipeline. A **trivial change** changes no
behavior, no layout, and no contract — wording, copy, comments, formatting.
For these, skip `ui-design`, `technical-design`, and `test-cases`:

- Implement directly.
- Write the minimal docs: update the spec only if the wording is a
  requirement; otherwise no artifact content changes.
- Record the change in the `## History` section of **every** artifact, even
  the ones the change did not touch.

The test is the same one that decides spec-vs-feature: *does this change
what the system does, what it looks like, or what it promises?* If yes, it
is not trivial — run the pipeline. If no, it is a wording change, and the
history is the only record it needs.

## Approval

Work advances through gates **in order**. Each gate opens only when the
previous artifact is `approved`:

```
spec → ui-design → technical-design → test-cases → implement → verify → deploy
```

Do not start a stage until its required input is approved.

A gate is approved only by a **human**, recorded in the artifact itself:

```markdown
Status: approved · <name> · 2026-11-02T14:03Z · sha256:ab12cd34
```

### The revision identifier

An approval covers **the specific revision the reviewer read**, so the
status line names that revision: a timestamp plus a content hash.

- The timestamp comes from the store — Outline's `updatedAt`, or the commit
  time in a repository
- The hash is `sha256` of the **body with the status line and the `## History`
  section stripped**. It cannot include the line that contains it, or writing
  the hash would change the hash; and the history is a log, not content, so
  updating it must not invalidate an approval
- Verification is mechanical: recompute, compare. A mismatch means `draft`,
  whatever the line claims

Why both: the timestamp detects *that* the artifact changed after approval,
the hash detects *whether the content* differs. Timestamp alone cannot tell
a formatting edit from a requirement edit; hash alone cannot tell when.

### Four status values

| Status | Meaning | Effect |
|---|---|---|
| `draft` | work in progress, not yet approved | the next stage may not begin |
| `approved` | a human approved this exact revision | proceed |
| `rejected` | the artifact is wrong — invented content, contradictions, outside its stage's remit | its author reworks it |
| `disagree` | the artifact is right, but the decision behind it is contested | escalate; nothing proceeds until ruled on |

`rejected` blames the author; resolve it with the author. `disagree` blames
the decision; resolve it with the owner of the decision. A spec author can
fix a rejection but cannot resolve a disagreement about their own
requirement — that goes above them.

Only `approved` advances the workflow. The other three all halt.

### Editing an approved artifact

**The edited revision becomes `draft`. The previous approval is not
withdrawn — it is history.**

A rejection does not erase the last approved baseline. Keep that baseline
available while the proposed change is corrected: in a repository it is the
commit the approval named; in Outline it is the last approved revision. This
matters at release time — you need something approved to fall back to while
the next revision is still being argued about.

Do not treat the old approval as approval of the edited content. The
baseline is where you were; the draft is where you are going.

### Sequential design approvals

`ui-design.md` is approved before `technical-design.md` is written. The
technical design is authored against approved UI decisions, so it cannot
guess at layout it has not seen approved.

- **The UI document is the earlier gate.** If the technical design finds the
  UI wrong, work returns to `ui-design.md` — the earliest artifact that needs
  correcting, not the nearest.
- **Withdrawal is scoped to the file.** Editing `technical-design.md` does
  not touch the UI approval. Editing `ui-design.md` invalidates the technical
  approval only where a transition the technical doc cites changed.

**The approval request ends your turn.** Write the artifact, summarize it,
list the open questions, ask the human to approve — then stop. Do not start
the next stage, do not draft the next document, do not write code in the same
turn, even if the work feels trivial. Starting early converts a gate into a
formality, and the human reviews work that is already committed.

**One gate has a second stop: `spec → ui-design`.** Approving the spec ends
the turn, and the next turn asks before it starts — the spec becomes screens
in pen.dev, under the designer, before this skill has a UI stage to run. See
Stage 1, *After the spec is approved*. The gap is not optional and not
shortcut by drafting `ui-design.md` from the spec.

## Boundaries

Standing permission, checked at every stage:

**Always**
- Record durable decisions in the artifact, not in local memory
- Run the repository's **aggregate** test command before reporting work
  complete — every unit, not only the one you touched. A unit the aggregate
  cannot reach is untested, however green the output looks
- Follow the target unit's existing conventions before introducing new ones
- Keep every approved artifact in version control
- Point at the `REQ`/`AC` a change serves

**Ask first**
- Changing an approved requirement, acceptance criterion, or flow edge
- Database schema or migration changes
- Adding a dependency or a new technology
- Changing CI, deployment config, or build tooling
- Touching a shared contract duplicated across units

**Never**
- Commit secrets, tokens, or credentials
- Weaken or delete a failing test to make work pass
- Declare completion without executed evidence
- Invent a requirement to fill a gap in the spec
- Edit `vendor/`, generated code, or another unit's files

These apply even when the spec is silent. A spec that would require
breaking a Never is a spec that needs the human, not a clever reading.

## Requirements that arrive vague

Translate them into measurable conditions before specifying, and have the
human confirm the translation.

```
REQUEST: "make the payment flow reliable"

REFRAMED:
- 100 sequential confirmations produce exactly 100 credits, no duplicates
- provider timeout leaves the intent recoverable, never silently failed
- two concurrent confirmations of one reference credit once
→ Are these the right targets?
```

Without this, "reliable" is unimplementable and unverifiable — and the
implementer decides what it means.


## Backward edges

When a later stage finds an earlier artifact wrong, work returns to the
**earliest artifact that needs correcting** — not to the one nearest the
discovery, and not to all of them.

| What is wrong | Return to |
|---|---|
| a behavior or requirement is wrong or missing | **spec** |
| behavior is right, but the screen or interaction is wrong | **ui-design** (if the intended behavior itself changed, the spec first) |
| behavior is right, but the technical approach is incomplete or wrong | **technical-design** |
| requirements and designs are correct, but verification is incomplete or a `TC` is wrong | **test-cases**, or implementation, as appropriate |

Routing to the earliest cause is what stops a fix from landing in the wrong
place. A wrong business rule patched in the technical design leaves the spec
asserting the wrong thing forever — the next reader trusts it.

### After an artifact changes

**Review every downstream artifact that depends on the changed content, and
keep every approval that is still valid.**

| Situation | Effect |
|---|---|
| downstream content and its references remain valid | **keep the approval** — do not churn a gate that did not change |
| downstream cites something that changed (a transition id, an `AC`, a contract) | that approval reverts |
| downstream is silently now inconsistent | re-review; the inconsistency is a finding |

Blaming every downstream artifact for every upstream edit is how approvals
become rubber stamps: a reviewer asked to re-approve unchanged text approves
without reading. Reverting only what actually depends on the change keeps
each gate meaningful.

**Do not deploy a candidate whose required downstream approvals are stale or
missing.** The revision verified must be the revision shipped.

### What the prototype cannot settle

When the ui-design stage reads Pencil or Figma and finds a screen or transition
the spec never describes, ask which fact kind is in dispute: a behavior the
spec omitted is the spec's gap (return to **spec**, re-approve); a layout
choice the spec never claimed is the designer's and needs no spec change.
The ruling goes in `DIV-###` and is marked inline in the design document.
Neither artifact is silently updated to match the other — see Truth and
authority.

## Fallback is system behavior, not workflow

Two different things share the word. Keep them apart:

- **Action fallback** — the system's behavior when the happy path fails:
  `QRIS expires → payment.failed, wallet not credited`. This is a
  **requirement**, it lives in the spec's flow table, and it needs an
  `AC`. Every failure branch in the flow is an action fallback.
- **Process fallback** — a stage sending work backward. That is the
  table above, and it never appears in a spec.

A spec containing process fallback is confused. A flow table without
fallback branches is incomplete — if the happy path has three ways to
fail, the table has four rows.

## Halting

Stop and ask the human when:

- An input artifact is not `approved`, or its body hash does not match the
  revision named in its status line
- **A spec was just approved and the human has not said whether to continue
  into UI design** — and, if they have not drawn the screens yet, until they
  do
- The UI stage is asked to begin but the canvas has no screens for this spec
- The UI design and technical design disagree about a transition
- Test cases were written after reading the implementation
- A `TC` expectation cannot be derived from the spec and design alone
- A flow transition has no `TC` — transition coverage is incomplete
- Two `AC` contradict each other
- A requirement cannot be satisfied without inventing business behavior
- The flow table has a transition whose `to` has no defined state
- The requested work does not map to any approved `REQ`
- A top-level prototype frame fits no inventory class
- Two frames claim the same route and neither is marked current
- A divergence was found and no `DIV-###` row exists
- A ruling changes behavior and no spec re-approval followed
- An agent is about to modify an existing prototype frame
- An agent is about to propose a missing screen on its own initiative, when
  the designer has not asked for one
- The request bundles several independently testable capabilities and no
  capability map has been approved
- A `TC` can only be observed in production — that is not a verifiable case
- A `TC` cannot be linked to an `AC`, or has no `TC-<feature>-###` id
- A `TC` declares no level, or a level the feature can be observed at has no
  `TC` and no coverage-map row saying so
- An approved `TC` has no automation and is absent from
  `reports/test-handover.md` — an unverified case with no home
- The approved cases were not pushed to planTestIt

Never resolve any of these by choosing a plausible answer. Guessing at a
requirement is the failure mode this skill exists to prevent.

## Rationalizations

| Thought | Reality |
|---|---|
| "The spec is obvious, I'll write it after" | Then it is a description of the code, not a requirement |
| "This change is too small for a spec" | Small means a short spec — one row. It does not mean no record |
| "I'll add the AC I need while implementing" | That is inventing a requirement. Route to design |
| "Tests pass, so the spec is satisfied" | Tests prove the test author's understanding, not the requirement's |
| "The design differs slightly from the spec, it's better" | Approval covers the spec. A better idea is a spec change |
| "I'll fix the spec directly from implement, it's faster" | It skips design and leaves the design stale |
| "The edge case is unlikely, I'll skip it" | Unlikely edges are the ones QA finds in production |
| "I'll draft the design while they read the spec" | The gate is the approval, not the artifact. End the turn |
| "The spec is approved, so UI design is next — I'll start" | Approved means the *input* is ready, not the screens. The designer draws in pen.dev first; ask, then stop |
| "I'll write the states table from the spec's flow and fill in node ids later" | Then it is a design of your own, and the designer's canvas is a third truth. `ui-design.md` records what resolves on the canvas |
| "The designer hasn't drawn it yet, so I'll design the screen" | Only when asked. A missing screen is a finding routed to spec, unless the designer requests the proposal |
| "It's one big feature, splitting is overhead" | A ten-line capability map is cheaper than a monolithic contract every task must reason over |
| "Engineering approved, the designer will catch up" | Both documents block the next stage. One approval is no approval |
| "I'll read the code first, then write the tests" | Then they describe what was built, not what was required. That is how a suite goes green on wrong behavior |
| "The test is wrong, I'll just fix the expected value" | A failing `TC` is a finding. Changing it needs approval, or you have deleted the requirement |
| "I implemented the TC, it passes" | Passing proves nothing. Show the automation fails for the right reason before the feature exists — or record why it cannot |
| "The frontend has no test runner, I'll note it and move on" | An unautomated approved `TC` is an unverified requirement. Record it as a finding; it is unverified, not passed |
| "Unit tests are the implementer's business, so nobody needs to see them" | Ungated is not invisible. The implementation report states what they cover, or a reviewer cannot tell zero from thorough |
| "The case has no harness, I'll drop it" | Dropping it deletes the requirement. It goes in `reports/test-handover.md` as unverified, with what would unblock it |
| "I'll write the unit test after reading the code" | Then it is white-box and belongs to the implementer. A contract-level `TC` is derived from the design, not the implementation |
| "Every level needs a case, so I'll add a system test" | Write it, but it cannot be executed here. `system` cases always land in the handover — Stage 6 runs them |

## Reference

- `README.md` — orientation: what each stage, artifact, and reference file is for, and which one to open
- `spec-template.md` — the artifact
- `design-ui-template.md` — UI document: frame inventory, states, transitions
- `design-technical-template.md` — technical RFC: architecture, SQL, endpoints
- `test-cases-template.md` — test design output
- `agents.md` — per-role read restrictions and halt conditions
- `repo-layout.md` — directory conventions and stack defaults