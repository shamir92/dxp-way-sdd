#!/usr/bin/env python3
"""Verify spec-driven-development artifacts in a repository.

Checks, in order of confidence:
  1. status vocabulary      — only draft/approved/rejected/disagree
  2. approval hash          — recompute and compare (advisory: see --strict)
  3. case traceability      — every TC id has an automation reference or a handover row
  4. stage presence         — every gated artifact a feature needs exists

Usage:
    sdd-verify.py [specs-dir] [--strict] [--quiet]

Exit codes:
    0  no findings
    1  findings (warnings only)
    2  findings under --strict
"""

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

VALID_STATUS = {"draft", "approved", "rejected", "disagree"}
GATED = ("spec.md", "technical-design.md", "test-cases.md")
CODE_GLOBS = ("*.go", "*.ts", "*.tsx", "*.js", "*.jsx", "*.rs", "*.py", "*.java")

TC_ID = re.compile(r"TC-[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}")
STATUS_LINE = re.compile(r"^Status:\s*(.+)$", re.M)
CLAIMED_HASH = re.compile(r"sha256:([0-9a-f]+)")


def strip_for_hash(text):
    """Body with the status line and the History section removed."""
    body = STATUS_LINE.sub("", text, count=1)
    body = re.split(r"^#{1,6}\s+History\s*$", body, flags=re.M)[0]
    return body


def hash_matches(claimed, text):
    body = strip_for_hash(text)
    for candidate in (body, body.strip(), body.strip() + "\n"):
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        if digest.startswith(claimed) or claimed.startswith(digest):
            return True
    return False


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def collect_code_refs(root):
    """TC ids referenced anywhere in source files."""
    refs = set()
    for glob in CODE_GLOBS:
        for path in root.rglob(glob):
            parts = set(path.parts)
            if parts & {"node_modules", "vendor", "dist", "build", ".git", "target"}:
                continue
            refs.update(TC_ID.findall(read(path)))
    return refs


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    strict = "--strict" in argv
    quiet = "--quiet" in argv
    specs = Path(args[0]) if args else Path.cwd() / "docs" / "specs"
    root = specs.parent.parent

    if not specs.is_dir():
        print(
            f"no artifact folder at {specs}\n"
            f"pass the path: sdd-verify.py <repo>/docs/specs",
            file=sys.stderr,
        )
        return 1

    findings = []
    notes = []
    code_refs = collect_code_refs(root)

    for feature in sorted(p for p in specs.iterdir() if p.is_dir()):
        name = feature.name
        present = {p.name for p in feature.glob("*.md")}

        # 1 + 2: status vocabulary and approval hash
        for md in sorted(feature.rglob("*.md")):
            text = read(md)
            match = STATUS_LINE.search(text)
            if not match:
                continue
            line = match.group(1).strip()
            word = re.split(r"[\s·—]", line, maxsplit=1)[0].lower()
            rel = md.relative_to(specs.parent.parent)

            if word not in VALID_STATUS:
                findings.append(f"{rel}: status '{word}' is not one of {sorted(VALID_STATUS)}")
                continue

            claimed = CLAIMED_HASH.search(line)
            if word == "approved" and not claimed:
                findings.append(f"{rel}: approved with no sha256 revision")
            elif claimed:
                if not hash_matches(claimed.group(1), text):
                    findings.append(
                        f"{rel}: approval hash does not match the body "
                        f"(claimed {claimed.group(1)[:16]})"
                    )

        # 4: stage presence (a feature that has a spec should declare its gates)
        if "spec.md" in present:
            for gated in GATED:
                if gated not in present and gated != "ui-design.md":
                    notes.append(f"{name}: no {gated}")

        # 3: case traceability
        cases_file = feature / "test-cases.md"
        if not cases_file.is_file():
            continue
        ids = set(TC_ID.findall(read(cases_file)))
        if not ids:
            continue
        handover = feature / "reports" / "test-handover.md"
        handed = set(TC_ID.findall(read(handover))) if handover.is_file() else set()
        orphan = ids - code_refs - handed
        if orphan:
            findings.append(
                f"{name}: {len(orphan)}/{len(ids)} approved cases have no automation "
                f"and no handover row (e.g. {sorted(orphan)[0]})"
            )

    for note in notes:
        print(f"note: {note}")
    if not quiet:
        for finding in findings:
            print(f"finding: {finding}")
        if not findings:
            print(f"ok: {specs} — no findings")

    if findings:
        return 2 if strict else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
