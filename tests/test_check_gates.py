"""Tests for check_gates.py — stdlib only.

    python3 -m unittest discover -s tests -v

Every test builds its own throwaway git repository in a temporary directory.
Nothing here knows where the repo was cloned: the checker and its fixtures are
resolved from this file's location.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[1] / "scripts" / "check_gates.py"
GIT = shutil.which("git")


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, check=True
    ).stdout.strip()


def run(repo, *args):
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "-r", str(repo), *args],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def failed(out):
    """The names of the checks that reported FAIL."""
    return re.findall(r"^\s+FAIL\s{2}(.+?)\s{2,}", out, re.M)


def phase(n, name, body="**Produces** — something.", gate=True):
    block = [f"## {n}. {name}", "", body, ""]
    if gate:
        block += ["**Gate** — met.", ""]
    return block


class Slice:
    """A temporary git repo holding one slice ledger."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        if GIT:
            git(self.root, "init", "-q")
            git(self.root, "config", "user.email", "test@example.com")
            git(self.root, "config", "user.name", "test")
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("def add(a, b):\n    return a + b\n")
        (self.root / "src" / "tests.py").write_text("def test_add():\n    assert True\n")
        if GIT:
            git(self.root, "add", "-A")
            git(self.root, "commit", "-qm", "base")
        self.base = git(self.root, "rev-parse", "HEAD") if GIT else "HEAD"
        # the change under test
        (self.root / "src" / "a.py").write_text(
            "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n"
        )

    def ledger(self, *, phases=None, closed=("src/a.py",), feel=True,
               extra="", test_command=None, max_files=None, max_lines=None):
        d = self.root / "Implementation" / "demo"
        (d / "evidence").mkdir(parents=True, exist_ok=True)
        (d / "evidence" / "baseline.txt").write_text("1 passed\n")
        command = test_command or f'{sys.executable} -c "import sys; sys.exit(0)"'
        note = [f"base: {self.base}", f"test-command: {command}"]
        if max_files is not None:
            note.append(f"max-files: {max_files}")
        if max_lines is not None:
            note.append(f"max-lines: {max_lines}")
        note.append("")
        note += ["```closed-files", *closed, "```", ""]
        for n, name, *rest in phases or DEFAULT_PHASES:
            note += phase(n, name, rest[0] if rest else "**Produces** — something.")
        if feel:
            note += ['feel-check: APPROVED — "ok" — 2026-10-27T09:00', ""]
        note += [extra, "evidence/baseline.txt", ""]
        (d / "note.md").write_text("\n".join(note))
        git(self.root, "add", "-A")
        return d / "note.md"

    def close(self):
        self._tmp.cleanup()


DEFAULT_PHASES = [
    (1, "VISION", "**Produces** — problem, outcome."),
    (2, "OUTWARD RESEARCH", "- finding `src/a.py:1`"),
    (3, "INWARD RESEARCH", "- map `src/a.py:1`"),
    (4, "ARCHITECT", "**Produces** — design."),
    (5, "SPLIT", "**Produces** — one lane."),
    (6, "DISPATCH", "**Brief anatomy** — scope."),
    (7, "VERIFY", "- `git diff` read"),
    (8, "INTEGRATE", "**Gate** — closed."),
]


@unittest.skipUnless(GIT, "git is required")
class CheckGates(unittest.TestCase):
    def setUp(self):
        self.slice = Slice()

    def tearDown(self):
        self.slice.close()

    def test_clean_ledger_passes(self):
        self.slice.ledger()
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 0, out)
        self.assertIn("phases 1,2,3,4,5,6,7,8 present", out)
        self.assertEqual(failed(out), [])

    def test_file_outside_closed_list_fails(self):
        self.slice.ledger()
        (self.slice.root / "src" / "intruder.py").write_text("x = 1\n")
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("closed file list", failed(out))
        self.assertIn("src/intruder.py", out)

    def test_untracked_residue_fails(self):
        self.slice.ledger()
        (self.slice.root / "probe_dump.json").write_text("{}\n")
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("scratch residue", failed(out))

    def test_skip_marker_fails(self):
        self.slice.ledger(closed=("src/a.py", "src/tests.py"))
        (self.slice.root / "src" / "tests.py").write_text(
            "import pytest\n\n@pytest.mark.skip\ndef test_add():\n    assert True\n"
        )
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("skip / focus markers", failed(out))

    def test_missing_gate_fails(self):
        phases = list(DEFAULT_PHASES)
        phases[3] = (4, "ARCHITECT", "**Produces** — design.")
        self.slice.ledger(phases=[(n, name, *rest) for n, name, *rest in phases])
        # strip the gate from ARCHITECT
        note = self.slice.root / "Implementation/demo/note.md"
        text = note.read_text().replace(
            "## 4. ARCHITECT\n\n**Produces** — design.\n\n**Gate** — met.",
            "## 4. ARCHITECT\n\n**Produces** — design.",
        )
        note.write_text(text)
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("4", out.split("missing gate:")[1].split("\n")[0])

    def test_duplicate_phase_heading_fails(self):
        self.slice.ledger(extra="## 1. VISION\n\n**Produces** — again.\n\n**Gate** — met.")
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("phase heading appears twice: 1", out)

    def test_receiptless_bullet_fails(self):
        phases = list(DEFAULT_PHASES)
        phases[2] = (3, "INWARD RESEARCH", "- a claim with no receipt at all")
        self.slice.ledger(phases=[(n, name, *rest) for n, name, *rest in phases])
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("receipts on claims", failed(out))

    def test_red_suite_fails(self):
        self.slice.ledger(test_command=f'{sys.executable} -c "import sys; sys.exit(3)"')
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("suite green", failed(out))

    def test_no_tests_flag_skips_suite(self):
        self.slice.ledger(test_command=f'{sys.executable} -c "import sys; sys.exit(3)"')
        code, out, _ = run(self.slice.root, "--no-tests")
        self.assertEqual(code, 0, out)
        self.assertIn("--no-tests", out)

    def test_missing_feel_check_fails(self):
        self.slice.ledger(feel=False)
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("feel-check recorded", failed(out))

    def test_ceiling_from_ledger_and_flag_override(self):
        self.slice.ledger(max_files=0, max_lines=400)
        code, out, _ = run(self.slice.root)
        self.assertEqual(code, 1)
        self.assertIn("files ledger", out)
        code, out, _ = run(self.slice.root, "--max-files", "5")
        self.assertEqual(code, 0, out)
        self.assertIn("files flag", out)

    def test_exit_two_without_ledger(self):
        shutil.rmtree(self.slice.root / "Implementation", ignore_errors=True)
        code, _, err = run(self.slice.root)
        self.assertEqual(code, 2)
        self.assertIn("no Implementation", err)

    def test_exit_two_with_several_ledgers(self):
        self.slice.ledger()
        shutil.copytree(
            self.slice.root / "Implementation/demo",
            self.slice.root / "Implementation/other",
        )
        code, _, err = run(self.slice.root)
        self.assertEqual(code, 2)
        self.assertIn("several ledgers", err)
        # disambiguated: it runs, and the sibling ledger's uncommitted files
        # are then residue outside this slice's closed list
        code, out, _ = run(self.slice.root, "--slug", "other")
        self.assertIn("ledger  Implementation/other/note.md", out)
        self.assertIn("closed file list", failed(out))

    def test_exit_two_outside_a_repo(self):
        plain = Path(self.slice._tmp.name) / "plain"
        plain.mkdir()
        code, _, err = run(plain)
        self.assertEqual(code, 2)
        self.assertIn("not a git repository", err)


if __name__ == "__main__":
    unittest.main()
