#!/usr/bin/env python3
"""check_gates.py — the mechanical half of the Implementation Discipline gates.

Reads git state and the slice ledger. Asserts what can be checked exactly and
prints, explicitly, what it could not check. Read-only: never writes, never
touches the network, stdlib only.

Exit 0 = no FAIL, 1 = at least one FAIL, 2 = cannot run (no repo / no ledger).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
FACTS, FORM = "facts from git", "form in ledger"

SKIP_PATTERNS = [
    r"\.skip\(",
    r"\bxfail\b",
    r"@Disabled\b",
    r"#\[ignore\]",              # rust
    r"\bt\.Skip\(",               # go
    r"\b(it|describe|test)\.only\(",
    r"pytest\.mark\.skip",
    r"\bskipIf\b",
    r"\.todo\(",
]

RECEIPT_PATTERNS = [
    r"[\w./\-]+\.[A-Za-z0-9]+:\d+",   # file:line
    r"https?://",                     # url
    r"`[^`]+`",                       # backticked command or path
    r"\(assumed\)",                   # explicit assumption tag
]

NOT_CHECKED = [
    "RED attribution (that the failing assertion is the missing behaviour)",
    "guard-kill correctness (that the killed guard is the one that failed)",
    "brief sufficiency (that a worker could execute it cold)",
    "design sufficiency (that SPLIT can cut it and DISPATCH can brief it)",
    "seam fidelity (that the pinned interfaces survived the merge)",
    "rendering truth (that a measurement asserts the right thing)",
    "whether the vision was right",
    "whether a recorded approval was genuine",
]


def sh(cmd, cwd):
    return subprocess.run(
        cmd if isinstance(cmd, str) else list(cmd),
        cwd=str(cwd),
        shell=isinstance(cmd, str),
        capture_output=True,
        text=True,
    )


def git(repo, *args, check=False):
    r = sh(["git", *args], repo)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def find_ledger(repo: Path, slug: str | None) -> tuple[Path | None, str]:
    base = repo / "Implementation"
    if not base.is_dir():
        return None, "no Implementation/ directory"
    if slug:
        p = base / slug / "note.md"
        return (p, "") if p.is_file() else (None, f"no ledger at Implementation/{slug}/note.md")
    found = sorted(p for p in base.glob("*/note.md"))
    if len(found) == 1:
        return found[0], ""
    if not found:
        return None, "no Implementation/*/note.md"
    names = ", ".join(p.parent.name for p in found)
    return None, f"several ledgers ({names}); pass --slug"


def section(text: str, number: int):
    m = re.search(rf"^## {number}\. .*$", text, re.M)
    if not m:
        return None
    start = m.end()
    nxt = re.search(r"^## ", text[start:], re.M)
    return text[start:start + nxt.start()] if nxt else text[start:]


def parse(text: str) -> dict:
    m = re.search(r"^base:\s*(\S+)", text, re.M)
    base = m.group(1) if m else None
    m = re.search(r"^test-command:\s*(.+)$", text, re.M)
    test_command = m.group(1).strip() if m else None
    m = re.search(r"```closed-files\s*\n(.*?)```", text, re.S)
    closed = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()] if m else None
    feel = re.search(r"^feel-check:\s*(\S+)(.*)$", text, re.M)
    evidence = sorted(set(re.findall(r"evidence/[A-Za-z0-9._\-]+", text)))
    return {
        "base": base,
        "test_command": test_command,
        "closed": closed,
        "feel": feel,
        "evidence": evidence,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanical checks for Implementation Discipline gates.")
    ap.add_argument("-r", "--repo", default=".", help="repo root (default: cwd)")
    ap.add_argument("--slug", help="slice slug under Implementation/")
    ap.add_argument("--no-tests", action="store_true", help="skip running the test command")
    ap.add_argument("--max-files", type=int, default=5)
    ap.add_argument("--max-lines", type=int, default=400)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    repo = Path(args.repo).expanduser().resolve()
    rows: list[dict] = []

    def add(group, check, verdict, detail):
        rows.append({"group": group, "check": check, "verdict": verdict, "detail": detail})

    if git(repo, "rev-parse", "--git-dir").returncode != 0:
        print(f"not a git repository: {repo}", file=sys.stderr)
        return 2
    ledger, why = find_ledger(repo, args.slug)
    if ledger is None:
        print(why, file=sys.stderr)
        return 2
    text = ledger.read_text(encoding="utf-8", errors="replace")
    meta = parse(text)
    ledger_dir = str(ledger.parent.relative_to(repo))
    ledger_rel = str(ledger.relative_to(repo))

    # 1 — base resolves
    if meta["base"]:
        ok = git(repo, "rev-parse", "--verify", f"{meta['base']}^{{commit}}").returncode == 0
        add(FACTS, "base resolves", PASS if ok else FAIL, meta["base"] + ("" if ok else " — unknown commit"))
    else:
        add(FACTS, "base resolves", SKIP, "no `base:` line in the ledger; slice not opened")

    # changed files
    changed: list[str] = []
    inside = {"files": 0, "lines": 0}
    if meta["base"]:
        names = [ln for ln in git(repo, "diff", "--name-only", meta["base"]).stdout.splitlines() if ln]
        untracked = [
            ln[3:] for ln in git(repo, "status", "--porcelain").stdout.splitlines() if ln.startswith("?? ")
        ]
        changed = names + [u for u in untracked if u not in names]

        def is_ledger(p):
            return p.startswith(ledger_dir + "/")

        outside = [p for p in changed if not is_ledger(p)]

        # 2 — closed file list
        if meta["closed"] is None:
            add(FACTS, "closed file list", SKIP, "no ```closed-files block in the ledger")
        else:
            allowed = set(meta["closed"]) | {p for p in changed if is_ledger(p)}
            intruders = [p for p in changed if p not in allowed]
            detail = (
                f"{len(outside)} changed outside the ledger, {len(intruders)} outside the closed list"
                + (": " + ", ".join(intruders[:8]) if intruders else "")
            )
            add(FACTS, "closed file list", FAIL if intruders else PASS, detail)

        # 3 — ceiling
        numstat = git(repo, "diff", "--numstat", meta["base"]).stdout.splitlines()
        for ln in numstat:
            parts = ln.split("\t")
            if len(parts) != 3:
                continue
            a, d, p = parts
            if is_ledger(p):
                continue
            inside["files"] += 1
            if a.isdigit() and d.isdigit():
                inside["lines"] += int(a) + int(d)
        tracked = {ln.split("\t")[-1] for ln in numstat if len(ln.split("\t")) == 3}
        inside["files"] += len([p for p in changed if p not in tracked and not is_ledger(p)])
        over = inside["files"] > args.max_files or inside["lines"] > args.max_lines
        add(
            FACTS,
            "cycle ceiling",
            FAIL if over else PASS,
            f"{inside['files']}/{args.max_files} files, {inside['lines']}/{args.max_lines} lines"
            + (" — decompose in ARCHITECT" if over else ""),
        )

        # 5 — skip and focus markers in the change
        diff = git(repo, "diff", "-U0", meta["base"]).stdout
        added = [ln[1:] for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
        hits = []
        for ln in added:
            for pat in SKIP_PATTERNS:
                if re.search(pat, ln):
                    hits.append(ln.strip()[:120])
                    break
        add(FACTS, "skip / focus markers", FAIL if hits else PASS,
            f"{len(hits)} added line(s) disabling or focusing tests" + (": " + "; ".join(hits[:5]) if hits else ""))

        # 6 — scratch residue
        residue = [u for u in untracked if not is_ledger(u)]
        listed = set(meta["closed"] or [])
        suspect = [p for p in residue if p not in listed]
        add(FACTS, "scratch residue", FAIL if suspect else PASS,
            f"{len(suspect)} untracked file(s) outside the closed list"
            + (": " + ", ".join(suspect[:8]) if suspect else ""))

    # 4 — red suite
    if args.no_tests:
        add(FACTS, "suite green", SKIP, "--no-tests")
    elif not meta["test_command"]:
        add(FACTS, "suite green", SKIP, "no `test-command:` line in the ledger")
    else:
        r = sh(meta["test_command"], repo)
        tail = (r.stdout + r.stderr).strip().splitlines()
        add(
            FACTS,
            "suite green",
            PASS if r.returncode == 0 else FAIL,
            f"`{meta['test_command']}` exit {r.returncode}"
            + (f" — {tail[-1][:160]}" if tail else ""),
        )

    # 7 — every phase section present carries its gate
    present = []
    gated, ungated = [], []
    for n in range(1, 9):
        body = section(text, n)
        if body is None:
            continue
        present.append(n)
        (gated if "**Gate**" in body else ungated).append(str(n))
    verdict = FAIL if ungated else (PASS if present else SKIP)
    add(FORM, "phase gates present", verdict,
        f"phases {','.join(map(str, present)) or 'none'} present; missing gate: {','.join(ungated) or 'none'}")

    # 8 — evidence refs resolve and are not empty
    gone, empty = [], []
    for ref in meta["evidence"]:
        p = ledger.parent / ref
        if not p.exists():
            gone.append(ref)
        elif p.stat().st_size == 0:
            empty.append(ref)
    bad = gone + empty
    if meta["evidence"]:
        detail = f"{len(meta['evidence'])} reference(s)"
        detail += f"; missing: {', '.join(gone)}" if gone else ""
        detail += f"; empty: {', '.join(empty)}" if empty else ""
        add(FORM, "evidence integrity", FAIL if bad else PASS, detail)
    else:
        add(FORM, "evidence integrity", SKIP, "no evidence/ reference in the ledger")

    # 9 — receipts on outward research, inward research and verify bullets
    offenders = []
    for n in (2, 3, 7):
        body = section(text, n)
        if body is None:
            continue
        for ln in body.splitlines():
            s = ln.strip()
            if not s.startswith("- "):
                continue
            if any(re.search(p, s) for p in RECEIPT_PATTERNS):
                continue
            offenders.append(s[:120])
    add(FORM, "receipts on claims", FAIL if offenders else PASS,
        f"{len(offenders)} bullet(s) without file:line, url, command or (assumed)"
        + (": " + "; ".join(offenders[:4]) if offenders else ""))

    # 10 — feel-check recorded (form only)
    if meta["feel"]:
        token = meta["feel"].group(1)
        ok = token.upper().startswith("APPROVED")
        add(FORM, "feel-check recorded", PASS if ok else FAIL,
            f"token `{token}`" + ("" if ok else " — not APPROVED"))
    else:
        add(FORM, "feel-check recorded", FAIL, "no `feel-check:` line — INTEGRATE has not happened")

    fails = [r for r in rows if r["verdict"] == FAIL]
    if args.json:
        print(json.dumps({"repo": str(repo), "ledger": ledger_rel, "rows": rows,
                          "fails": len(fails), "not_checked": NOT_CHECKED}, indent=2))
    else:
        print(f"repo    {repo}")
        print(f"ledger  {ledger_rel}")
        if meta["base"]:
            print(f"base    {meta['base']}")
        for group in (FACTS, FORM):
            group_rows = [r for r in rows if r["group"] == group]
            if not group_rows:
                continue
            print(f"\n{group.upper()}")
            for r in group_rows:
                print(f"  {r['verdict']:<4}  {r['check']:<22}  {r['detail']}")
        print("\nNOT CHECKED")
        for item in NOT_CHECKED:
            print(f"  - {item}")
        print(f"\n{len(fails)} FAIL" if fails else "\nno FAIL — the mechanical half is clean; the gates are still yours to close.")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
