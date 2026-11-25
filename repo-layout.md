# Repository layout

Flat root, one product per repository. The shape below is a convention,
not a constraint the skill enforces — but the skill resolves every path
from a spec's `Targets:` field, so a spec naming a path that does not
exist is a defect.

```
docs/
  specs/
    <feature>/
      spec.md
      ui-design.md
      technical-design.md
      test-cases.md
      tech-debt.md
      reports/
        implementation.md
        test-handover.md
        verification.md
      design-evidence/
<name>/                 ← the product, e.g. lp/
  PROJECT.md            units, stack, ownership
  backend/              Go + Gin
  frontend/             Next.js (App Router)
  worker/               auxiliary unit
```

Legacy flat artifacts (`docs/specs/2026-11-01-<feature>.md`) stay valid
where they exist; migrate a feature into its folder the next time it is
edited, not as a batch.

## Units

`backend/` is required. Clients (`frontend/`) and auxiliary units
(`worker/`, `scheduler/`) are declared in `PROJECT.md`, not inferred from
folder names. A client is optional; a mobile client, when one exists, is
declared the same way.

**Units are independent.** No shared code between `backend/`, `frontend/`, and
`worker/` unless the spec says otherwise. Where that is a standing rule it
has a cost that must be paid deliberately: shared
logic is duplicated by design, so any contract change lands in every unit
that has a copy. A spec touching a duplicated contract must name every
unit it changes.

**Auxiliary units are first-class.** `worker/` is not a subdirectory of
`backend/` — it is its own module with its own build, its own config, and
its own tests. Treating it as an afterthought is how it ends up untested.

## Stack defaults

| Layer | Default | Override |
|-------|---------|----------|
| Backend | Go + Gin | state the alternative and why in the spec |
| Frontend | Next.js, App Router | prefer App Router unless the spec gives a reason not to |
| Database | PostgreSQL | state the alternative and why |

Additional technology (queue, cache, object storage, search) is chosen
per feature and **must be named in the spec's Constraints section**
with the constraint that requires it. A new dependency introduced during
implementation without a spec entry is a design change — route backward.

## When this layout stops fitting

A second backend means `<name>/` gains a sibling unit, which the flat root
already supports. A second product means a sibling of `<name>/` at the
root — also supported. What the flat root does not support is **shared
code across products**; if that need appears, that is the moment to
introduce a shared module — as an explicit migration with its own spec,
not as a quiet reorganization during unrelated work.

## PROJECT.md

Minimum viable content:

```markdown
# <name>

## Units
| Path | Kind | Stack | Owner |
|------|------|-------|-------|
| backend | api | Go 1.26 + Gin | <owner> |
| frontend | client | Next.js 16 App Router | <owner> |
| worker | auxiliary | Go 1.26 | <owner> |

## Shared contracts
Anything duplicated across units, and where each copy lives.

## Commands
Build, test, run for each unit. Name the aggregate test command first:

| Task | Command |
|------|---------|
| All tests | `make test-all` |
| backend tests | `make test` |
| worker tests | `make test-worker` |
```

## One command that runs every unit's tests — required at init

A repository must have **one command that runs every unit's tests** before
its first commit. This is not a convenience; it is the only thing that stops
a unit from being silently untested.

The failure mode is concrete and common. Units are independent modules, so
`go test ./...` run from one of them can never reach another. A `test-all`
that wraps only the backend reports success while the worker's entire suite
never runs — and nothing in the output says so. The target is wrong, the
build is green, and the gap is invisible until someone changes the worker.

Rules for that command:

- **Every declared unit is reachable from it.** A unit it cannot reach is a
  finding at init, not an assumption.
- **It fails if any unit fails.** No `|| true`, no continue-on-error, no
  "best effort". A target that swallows a failure is worse than no target.
- **A unit with no tests answers `no test files`.** Silence is not an
  answer; it is indistinguishable from a unit that was skipped.
- **Its description names what it actually runs.** A target called
  `test-all` that skips a unit is a lie the next reader believes.

CI should call that same aggregate command. If CI runs something narrower —
a build only, a single unit — record it in `tech-debt.md` with the trigger
that makes it urgent, because an automation nothing runs is unverified.

At init the aggregate command is the deliverable, not the individual
targets. Per-unit targets are how the aggregate is built, not how it is
verified.
