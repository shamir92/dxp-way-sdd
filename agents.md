# Agent roles

Not personas. **A contract**: what each role must read, may never read, must
produce, and when it stops.

The read restriction is the load-bearing part. An agent's independence in
this pipeline does not come from who it claims to be — it comes from what
it was allowed to see. An implementer reviewing its own requirement saw the
requirement and the code, and cannot tell them apart.

---

## Roles

### Spec author

| | |
|---|---|
| **Reads** | the problem statement, human answers, prior related specs |
| **Never reads** | design, test cases, implementation |
| **Produces** | `docs/specs/<feature>/spec.md` from `spec-template.md` |
| **Approved by** | PM / business owner |
| **Halts when** | the request bundles several independently testable capabilities and no capability map is approved; an assumption is uncorrected; an open question remains |

The spec author writes *what is required*, never *how it will be built*. A
spec describing a component or a library has overstepped into design, and
will be approved by someone who cannot evaluate that choice.

### UI design

| | |
|---|---|
| **Reads** | the approved spec, **the screens the designer has already drawn in pen.dev** (Pencil `.pen` or Figma MCP) |
| **Never reads** | implementation |
| **Produces** | `docs/specs/<feature>/ui-design.md` from `design-ui-template.md`: a frame inventory covering every top-level frame, states with per-row checked evidence, the transition table (when there is a screen), and `DIV-###` markers |
| **Approved by** | product designer |
| **Halts when** | the spec was approved but the human has not said whether to continue into UI design; the canvas has no screens for this spec (design happens in pen.dev, outside this session); a prototype transition is not in the spec (`ui-design → spec`); a needed state has no prototype screen (`ui-design → spec`, unless the designer asks for a proposal); a frame fits no inventory class; two frames claim one route with no current marker; a divergence has no `DIV-###` row; asked to modify an existing frame |

Extraction, not invention. Authority is per fact: the prototype owns layout
composition, the spec owns behavior. A divergence is a `DIV-###` row, never
a silent choice — and never a justification for editing a frame.

**This role begins after the designer's pen.dev session, not after the spec's
approval.** The agent does not design the screens: it opens the canvas the
designer produced through MCP, resolves what is there, and records it in
`ui-design.md`. Finding the canvas unchanged is a halt — the stage has not
started — not an invitation to design from the spec.

Writes to the prototype are **additive only**: insert a new draft frame the
designer asked for, or do nothing. Existing frames are never modified or
deleted, because the mutation does not persist — an agent that "fixes" a
frame leaves a change nobody can verify and a file that still says the old
thing.

### Technical design

| | |
|---|---|
| **Reads** | the approved spec, existing code and conventions, and the UI doc's flow table when one exists |
| **Never reads** | test cases, implementation of *this* feature |
| **Produces** | `docs/specs/<feature>/technical-design.md` from `design-technical-template.md` — begins only after `ui-design.md` is approved |
| **Approved by** | engineering lead, independently of the UI approval |
| **Halts when** | an `AC` cannot be satisfied without a decision the spec doesn't cover (`technical-design → spec`); the UI design and technical design disagree |

Reading existing code is allowed and expected — you cannot design a
migration without knowing the schema. Reading *the implementation of the
feature being designed* is not, because nothing exists yet and what does is
someone's starting draft.

**Transition ids are cited, never defined.** The technical doc references
`t3` from whichever document owns the flow, and never restates the table.
If a cited transition changes, this document's approval reverts — which is
why the citation rule is stricter than it looks.

### Test designer

| | |
|---|---|
| **Reads** | the approved spec, the approved UI design and technical design |
| **Never reads** | **implementation, the diff, the plan, the implementing agent's report** |
| **Produces** | `docs/specs/<feature>/test-cases.md` from `test-cases-template.md`, listing what it read, with a declared level per case — including **contract-level unit** cases, which assert a component contract the design already names; then — once approved — the same cases pushed to planTestIt keyed by `TC-<feature>-###` |
| **Approved by** | a human who is **not** the technical design owner |
| **Halts when** | an expectation cannot be derived from spec and design alone; a flow transition has no testable outcome; the design does not say what is observable; a level the feature can be observed at has no case |

**The strictest restriction in this pipeline, and the one most likely to be
violated accidentally** — the implementation is usually in the same working
tree. An agent that peeks produces assertions describing what was built,
and the suite goes green on wrong behavior.

The `Sources read:` line in the output exists so a reviewer can check.

**The line this role draws inside "unit test".** A unit case here asserts a
*contract* — given this fixture, this component returns that. The design's
Architecture section names the components, so the case is derivable without
reading code. A unit test that asserts *how* a component does it — mock
expectations, call counts, a private helper's edge case — is not derivable
from any design, and belongs to the implementer. If a contract-level case
cannot be written without reading the implementation, the design is
under-specified: that is `test design → technical-design`, not a licence to
peek.

### Implementer

| | |
|---|---|
| **Reads** | the approved UI design and technical design, the approved test cases, repository conventions |
| **Never reads** | — |
| **Produces** | code; one automation per approved `TC` (contract-level unit, integration, acceptance); **internal unit tests** of its own design; `reports/test-handover.md` for every approved `TC` it could not automate; executed evidence |
| **Approved by** | code review; completion requires evidence, not a claim |
| **Halts when** | a `TC` is ambiguous; the design is silent on an approved `AC` (`implement → technical-design`) |
| **Records as a finding** | a `TC` with no automation, or one that cannot be made to fail first — unverified, not passed; written to `reports/test-handover.md`, never dropped |

The only role with no read restriction, because it must see everything to
build correctly. That is exactly why it is the role that must not verify
its own work.

**It owns both unit kinds, and the difference is authorship, not effort.**
Contract-level unit cases come from the approved test design and are gated;
internal unit tests are its own judgment and are ungated. The ungated ones
are still **reported** — `reports/implementation.md` states what they cover,
so "the implementer wrote no unit tests" is visible rather than assumed.

**`system`-level cases are never implemented here.** They need a running
environment, which this stage does not have. They go straight to
`reports/test-handover.md` for Stage 6.

### Verification tooling — outside this skill

Execution is separate tooling: cases run against a running environment and
results live in planTestIt. The skill's obligation ends at pushing approved,
`AC`-linked, id-keyed cases and recording the run reference.

Two constraints stay here because they are about the artifact, not the tool:

- Results are **never written back** into an approved `test-cases.md` — that
  would invalidate its approval
- A case with no result and no automation is a **finding**, not a pass

### Test runner — not yet defined

Execution is a separate skill, not yet written. When it exists it will own
running the cases, seeding fixtures, and reporting results. Two constraints
are already fixed, so the runner does not design itself into an awkward
corner later:

- It **reads** approved test cases and **writes a separate evidence
  report** — never into the approved file, which would invalidate its
  revision-validated approval (timestamp + body hash)
- Its results are keyed by `TC-<feature>-###`

Until it exists, "tests pass" is the implementer's claim backed by the
command and its output — the implement stage's evidence requirement, not a
verification pass.

---

## The table that matters

| Role | Must not verify |
|---|---|
| Spec author | its own requirements |
| Technical design | its own architecture |
| **Implementer** | **its own implementation** |
| Test designer | never sees either, so cannot collude with both |

Independent verification requires two things: a **different context** (a
fresh session) and a **different input** (artifacts, not the previous
agent's summary). A reviewer given the implementer's report is reviewing
the report.

## Dispatch

When several agents work one feature in parallel — a service boundary, a
UI surface, an integration — each gets its own working tree and its own
briefing containing only its row above plus its ticket's `AC`/`TC` ids.

An agent that reads a sibling's ticket starts implementing it. That is not
enthusiasm; it is an agent filling the context it was given.
