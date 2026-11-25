# Spec-Driven Development (SDD)

A pipeline for turning a requirement into shipped code through **approved
artifacts**, with governed backward edges when a later stage finds an earlier
one wrong — and never sideways.

This is a working method, not a finished product. It is used on real features,
it is being developed in public, and this document records both what it does
and where it still leaks. See [Known gaps](#known-gaps).

---

## Install

Agents discover skills from a directory of `SKILL.md` folders. Drop this
repository in as one skill:

```bash
git clone https://github.com/shamir92/dxp-way-sdd.git \
  .agents/skills/spec-driven-development
```

Then invoke `/spec-driven-development`, or let the agent load it when a request
needs a spec before code.

Check conformance in your own tree:

```bash
python3 .agents/skills/spec-driven-development/sdd-verify.py docs/specs
```

Requires Python 3.8+. No dependencies.

---

## The problem it solves

An agent given a task will fill every gap in it. A vague requirement becomes a
chain of plausible decisions made by whoever wrote the code — and every one of
those decisions is invisible, because nobody was ever asked to object to it.
The code compiles, the tests pass, and the wrong premise has been in production
for three weeks.

The failure is not dishonesty. It is that **an unexamined assumption is the
most expensive kind of misunderstanding, because it survives review.** You
cannot object to a sentence that was never written.

SDD's answer: make every premise an artifact a human has read and signed, and
make each stage's input a document rather than a summary of a conversation.

---

## The pipeline

```
spec ──► ui-design ──► technical-design ──► test-cases ──► implement ──► [external verification]
  ▲           ▲                ▲                 ▲              │
  │           │                │                 │              │
  └─ behavior ┴─ screen/UI ────┴─ technical ─────┴── cases ─────┘
     wrong       wrong            approach          incomplete
                                  wrong
```

Each gate opens only when the previous artifact is `approved`. `ui-design` is
skipped when the feature has no screen.

**One handoff is held by a human, not by a status line.** After the spec is
approved the pipeline does not slide into UI design: the spec goes to the
design tool, the designer draws there, and UI design starts from that canvas
coming back through MCP. So the agent **asks** — "continue to UI design, or
take the spec to the design tool first?" — and stops until answered.

---

## What each stage does

| # | Stage | Question it answers | Produces | Skipped when |
|---|---|---|---|---|
| 0 | **Scope check** | is this one capability or several? | nothing, or a capability map in chat | the request is one capability |
| 1 | **Spec** | what must be true, in business language? | `spec.md` | never |
| 2 | **UI design** | what does the screen do? | `ui-design.md` | the feature has no UI surface |
| 3 | **Technical design** | how will it be built, and what else could have been? | `technical-design.md` | never |
| 4 | **Test design** | how do we know it works — without reading the code? | `test-cases.md` | never |
| 5 | **Implement** | write it to the approved design | code, automations, reports | never |
| 6 | **Verification** | does it actually work, against a real environment? | `reports/verification.md` | never — but it is **external** |

### Stage 0 — scope check

Most requests describe one capability. This stage exists for the exception: a
request that bundles several independently testable capabilities gets a
capability map approved *before* any spec is written. Decomposition is not a
planning detail — by the time you are planning, the oversized artifact already
exists and every downstream task must reason over the whole contract.

**Blocks on.** Several independently testable capabilities and no approved map.

### Stage 1 — spec

States what must be true, for whom, and what it costs today. Written by a human
decision, not by the implementer. Every guess is stated as an assumption and
confirmed *before* the spec is written.

**Must not contain.** Endpoints, field names, status codes, table names,
mechanisms, or test cases. A product owner naming a status code is approving a
contract they cannot evaluate, and design then inherits a decision it never
made.

**Blocks on.** An open question; an uncorrected assumption; an acceptance
criterion whose `Then` is not observable from outside; a flow table missing a
failure branch.

### Stage 2 — UI design

Extracts only what the record needs — states, transitions, and the node ids
that resolve — and points at the prototype. The screen is the source of truth
for layout; this document is not a redraw.

**Starts from the designer's canvas, not from the spec.** The approved spec is
taken to the design tool, the designer draws the screens there, and this stage
opens that result through MCP and records it. No screens on the canvas means
the stage has not started — ask, don't design.

**Must not.** Modify an existing prototype frame. Design tools are shared,
multiplayer documents; overwriting a designer's work is destructive and
unversioned. New frames are additive and marked draft.

**Blocks on.** A spec approved with no answer on whether to continue; a canvas
with no screens for this spec; a transition the prototype shows but the spec
never describes (a `DIV-###` ruling, routed to spec); a frame that fits no
inventory class.

### Stage 3 — technical design

Lets a reviewer disagree with the *approach* before code exists. RFC-shaped:
options considered, trade-offs accepted, open questions.

**Must not.** Be a plan. No task breakdown, no ordering, no estimates — a
design that sequences work becomes a second plan saying "do this in this
order." It also does not restate the spec or the flow table; it cites them by
id.

**Blocks on.** An acceptance criterion with no design element; a spec
constraint with no enforcement; an open question; a cited transition id that
does not exist.

### Stage 4 — test design

Defines how each approved requirement and each flow transition is verified —
**without reading the implementation**.

**The rule that makes it work.** The test-design agent may read the spec and
the design. It may not read the implementation, the diff, the plan, or the
implementing agent's report. Reading the code produces assertions describing
what was built rather than what was required, and the suite goes green on wrong
behavior.

The ordering enforces it: implementation has not started, so there is no code
to read. The `Sources read:` line in the output makes it auditable when the
ordering is violated.

**Three coverage axes, all mandatory.** Requirements, transitions (flow rows),
and **levels** (`unit` / `integration` / `system` / `acceptance`). Transition
coverage matters more than criterion coverage: criteria are written by the spec
author, so a branch the author forgot is invisible to that axis and
covered-looking. The flow table is the completeness check on the spec.

### Stage 5 — implement

Writes code to the approved design, satisfying the approved cases. The exit
condition is *"code merged, the implementer's own tests pass, a deployable
candidate exists"* — **not** "verified."

**Four deliverables.** Case automations (gated by test-design approval);
internal unit tests (ungated, but reported); `reports/test-handover.md` for
every case it could not automate; executed evidence — the command and its
output, never a conclusion.

**The automation must fail first.** Automate the case, run it, watch it fail
for the right reason, then implement. An assertion written after the feature
exists is written to pass.

### Stage 6 — verification (external)

Runs the approved cases against a running environment. **This skill does not
run anything.** Its obligation ends at handing over approved, traceable,
id-keyed cases and recording the run reference.

---

## Artifacts

One current set per feature, in `docs/specs/<feature>/`.

| Artifact | Records | Gated | Never contains |
|---|---|---|---|
| `spec.md` | intent, behavior, requirements, criteria, flow, constraints, `DIV-###` | yes | endpoints, fields, mechanisms, test cases |
| `ui-design.md` | screen states, transitions, resolvable node ids | yes | a redraw, or a description of what the screen looks like |
| `technical-design.md` | architecture, contracts, migrations, endpoints, options, trade-offs | yes | a plan, or a restatement of the spec |
| `test-cases.md` | how each criterion, transition, and level is verified | yes | anything derived from reading the code |
| `tech-debt.md` | what was deferred, why, and the trigger that makes it urgent | yes | a divergence — that is a `DIV-###` in the spec |
| `reports/implementation.md` | what changed, deviations, commands run, unit-test coverage | no | a claim without the command and its output |
| `reports/test-handover.md` | every approved case the implement stage could not automate | no | a case marked as passed |
| `reports/verification.md` | the run link, who verified, which revision | no | per-case results — those stay in the tool |
| `plan.md` | working aid, regenerable at will | **no** | a decision the design does not cover |

**Gated** means it carries a `Status:` line and blocks the next stage. Reports
and the plan do not. Reports are still artifacts: they carry `## Summary` and
`## History` like everything else, so opening one alone shows what that file
records and how it changed.

**Debt is not a divergence.** Debt is deferred work (`tech-debt.md`); a
`DIV-###` is a decided disagreement between two artifacts (the spec). Different
lifecycles, so different homes.

---

## How a gate is approved

A gate is approved only by a **human**, recorded in the artifact itself:

```markdown
Status: approved · <name> · 2026-11-02T14:03Z · sha256:ab12cd34
```

The intent of the hash is that approval covers **the specific revision the
reviewer read** — so a later edit demotes the artifact to `draft` instead of
quietly inheriting the old signature. The timestamp detects *that* the artifact
changed; the hash detects *whether the content* differs.

| Status | Meaning | Effect |
|---|---|---|
| `draft` | work in progress | the next stage may not begin |
| `approved` | a human approved this exact revision | proceed |
| `rejected` | the artifact is wrong — invented content, contradictions, outside its remit | its author reworks it |
| `disagree` | the artifact is right, but the decision behind it is contested | escalate; nothing proceeds |

`rejected` blames the author; resolve it with the author. `disagree` blames the
decision; resolve it with the owner of the decision.

**The approval request ends the turn.** Write the artifact, summarize it, list
the open questions, ask — then stop. Starting the next stage in the same turn
converts a gate into a formality.

---

## Truth and authority

There is no single authoritative document. Authority is **per fact**, and which
artifact wins depends on what kind of fact is in dispute — never on which file
was edited last.

| Fact kind | Authority | Cannot be overridden by |
|---|---|---|
| business intent, behavior, scope | **spec** (approved) | a prototype frame |
| layout composition | **prototype** (designer) | spec prose |
| technical shape — contracts, schema, layering | **technical design doc** | prototype |
| what exists today | **code** | any document |
| how a disagreement was settled | **the spec's `DIV-###` ledger** | nothing implicit |

This is the part that makes the method usable on real teams. Disagreement is
not automatically a fallback — find which fact kind is in dispute, then ask who
owns that kind. Routing everything to the spec asks a product owner to
re-approve a document to fix something that was never business-owned.

---

## Backward edges

When a later stage finds an earlier artifact wrong, work returns to the
**earliest artifact that needs correcting** — not to the one nearest the
discovery, and not to all of them.

| What is wrong | Return to |
|---|---|
| a behavior or requirement is wrong or missing | **spec** |
| behavior is right, but the screen or interaction is wrong | **ui-design** (if the intended behavior itself changed, the spec first) |
| behavior is right, but the technical approach is incomplete or wrong | **technical-design** |
| requirements and designs are correct, but verification is incomplete | **test-cases**, or implementation |

Routing to the earliest cause is what stops a fix from landing in the wrong
place. A wrong business rule patched in the technical design leaves the spec
asserting the wrong thing forever — and the next reader trusts it.

**After an artifact changes, review every downstream artifact that depends on
it, and keep every approval that is still valid.** Reverting only what actually
depends on the change keeps each gate meaningful. Blaming every downstream
artifact for every upstream edit is how approvals become rubber stamps.

---

## Reference files

| File | What it is for | Open it when |
|---|---|---|
| `SKILL.md` | the authority — every rule, stage, and halt condition | always; this README is only a map |
| `agents.md` | per-role contracts: what each role reads, may never read, and halts on | dispatching an agent, or checking whether a role may look at something |
| `spec-template.md` | the spec artifact, plus its self-check | writing or reviewing a spec |
| `design-ui-template.md` | frame inventory, states, transitions, evidence rows | writing a UI design document |
| `design-technical-template.md` | the RFC shape: architecture, SQL, endpoints, acceptance mapping | writing a technical design |
| `test-cases-template.md` | coverage maps, case fields, handover, self-check | writing test cases |
| `repo-layout.md` | directory conventions, stack defaults, and the aggregate-test-command rule | deciding where a file goes, what a unit is, or starting a repository |
| `sdd-verify.py` | checks approval hashes, status vocabulary, and case traceability | before claiming a stage is complete, or in CI |

### Which file do I open?

| I want to know… | Open |
|---|---|
| what the feature must do | `spec.md` |
| what the screen does | `ui-design.md`, then the prototype |
| how it is built | `technical-design.md` |
| how it is verified | `test-cases.md` |
| what was deliberately left undone | `tech-debt.md` |
| what actually changed | `reports/implementation.md` |
| which approved cases are unverified | `reports/test-handover.md` |
| whether it passed, and where | `reports/verification.md` |
| who may read what | `agents.md` |
| why a rule exists | `SKILL.md` |

---

## What this skill deliberately does not do

- **Decide what to build.** That is `brainstorming`. This skill records what
  was agreed and controls what may be built from it.
- **Run tests.** Execution is external tooling against a running environment.
- **Plan the work.** Task order and estimates are `writing-plans`. A design
  that sequences work is a second plan.
- **Verify its own output.** The implementer never verifies its own work; the
  test designer never sees the implementation.

---

## Starting a repository

Before the first commit, a repository needs **one command that runs every
unit's tests**. Units are independent modules, so `go test ./...` run from one
of them can never reach another — an aggregate that wraps only the backend
reports success while the worker's whole suite never runs, and nothing in the
output says so.

The aggregate command is the deliverable at init, not the per-unit targets. See
`repo-layout.md` § *One command that runs every unit's tests*.

---

## Known gaps

This skill is a live document. These are the places where a rule is written but
not yet enforced, recorded honestly rather than omitted — a method that claims
total conformance is a method nobody is measuring.

| Gap | What it means in practice | Status |
|---|---|---|
| **The approval hash is advisory** | Recomputing the hash under every plausible stripping rule does not reproduce the claimed value in most artifacts, and truncation is inconsistent (some 8 hex chars, some 16). The skill says verification is "mechanical: recompute, compare" — it is now mechanical, but the archives predate the checker | **Detected now** by `sdd-verify.py`; existing artifacts need re-approval to become valid |
| **Unautomated cases have no enforced home** | A rule says every approved case that cannot be automated must be listed in `reports/test-handover.md`. Adherence varies widely across features — some hand over nearly everything, some hand over nothing while claiming verification | **Detected now** by `sdd-verify.py`; enforcement is still review, not a hard block |
| **Stage 6 has never run** | `reports/verification.md` is in the pipeline diagram and listed as "never skipped," but no such file exists in any feature folder. The external runner is not built | **Blocked on tooling** |
| **Levels can be impossible to observe** | `system` is defined as external-only and "always lands in handover." A unit with no test runner therefore cannot observe most levels — so the rule "every level the feature can be observed at needs a case" ends up mandating cases that cannot run | **Needs harness declaration.** Which levels a unit can observe belongs in `repo-layout.md`, not discovered after authoring |
| **Independence assumes two humans** | The model rests on approvals by *different people* — the test designer must not be the technical design owner. Where one person holds every role, `rejected` and `disagree` route to the same desk and the distinction dies. Read restrictions are also self-reported by the agent being restricted | **Unaddressed.** The honest position for a solo operator is to record that the gate was self-approved |
| **Documents grow past reviewable size** | The method's premise is that an unexamined premise survives review — yet a large feature can produce thousands of lines across its artifact set, which nobody reads closely. It has optimized itself into the failure mode it warns about | **Needs size budgets** per artifact, with overflow moved to reference appendices excluded from the approval hash |
| **Status vocabulary has drifted** | Values beyond the documented four appear in practice (`superseded`, `implemented`, `not gated`). Reports sometimes carry a `Status:` line the skill says they do not have | **Needs a closed enum** a validator can reject |
| **`SKILL.md` is large enough to crowd out the task** | Over 1,100 lines load before any work begins, competing with the actual problem for context | **Needs progressive disclosure** — a short core plus reference files loaded on demand, as the templates already are |

The first two are the ones that matter most, and they now have a checker:
**`sdd-verify.py`** recomputes every claimed approval hash, rejects status
values outside the documented four, and traces every approved case to either an
automation reference in source or a row in `reports/test-handover.md`. It
reports findings — it does not fix them, and it does not yet block a merge.

```bash
python3 sdd-verify.py docs/specs   # findings exit 1
python3 sdd-verify.py --strict     # findings exit 2
```

Run it before claiming a stage is complete. Until the remaining rules have
checkers of their own, treat this skill's gates as **review discipline backed
by an incomplete check, not enforcement.**

### Current state

Measured with `sdd-verify.py` against the twelve features of the codebase this
method was developed in, at the time of writing. These numbers are meant to
move — re-run the checker against your own tree rather than trusting them.

| Measure | Value |
|---|---|
| Features with an artifact folder | 12 |
| Approval hashes that do not reproduce | most approved artifacts |
| Status values outside the documented four | 4 (`superseded`, `implemented`, `handover`, `not gated`) |
| Approved cases with no automation and no handover row | 193 of 446 |

The last row is the one to watch. It is not a formatting problem: a case in
that count is an approved requirement that nothing executes and nothing
records, which is precisely the state the method exists to prevent.

---

## Contributing

The most useful contribution is not a new rule — it is a counterexample. If a
rule here failed you, or you broke one and found the failure benign, that is
the evidence this document is missing. See `SKILL.md` § *Rationalizations* for
the excuses the method already anticipates, and § *Halting* for the conditions
it stops on.
