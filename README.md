# Implementation Discipline

A seven-phase pipeline for coding agents. Each phase has its own gate; a gate admits exactly one thing — entry into the next phase. Nothing is greenlit wholesale, no phase opens early, no phase is skipped silently.

```
VISION → RESEARCH → ARCHITECT → SPLIT → DISPATCH → VERIFY → INTEGRATE
```

| phase | decides |
|---|---|
| VISION | what is being built, for whom, and what "done" looks like — one question at a time, until a clean restatement carries no hedging |
| RESEARCH | what already exists: the code, the installed dependencies, the field. Inward and outward, with receipts |
| ARCHITECT | the design at function level, and whether the undertaking needs cutting into slices before it is designed at all |
| SPLIT | how the current slice is cut into lanes that cannot collide |
| DISPATCH | the brief each lane gets, and who reports a blocker to whom |
| VERIFY | proof by execution: read the diff, run the suite, kill a guard, walk the user's path |
| INTEGRATE | merge in order, check the pinned seams, take the feel-check, commit |

Two ideas do the heavy lifting. **Gates are phase-local** — an approval means "enter the next phase", never "the whole thing is approved". And **slices are bounded** — an undertaking estimated above ~5 files or ~400 changed lines is cut into slices, each of which is a full run of the same pipeline and leaves the system working.

## Install

Hermes Agent, keeping one copy:

```bash
git clone https://github.com/sirEven/implementation-discipline ~/Software/projects/implementation-discipline
ln -s ~/Software/projects/implementation-discipline \
      ~/.hermes/skills/software-development/implementation-discipline
```

Any other agent that reads the [agentskills.io](https://agentskills.io/specification) format: copy the directory into that tool's skills folder. The frontmatter is spec-compliant; the Nous-specific keys live under `metadata.hermes` and are ignored elsewhere.

## The mechanical half

`scripts/check_gates.py` checks only what a machine can check exactly — closed file list, cycle ceiling, red suite, skip and focus markers, scratch residue, a gate under every phase present, evidence integrity, receipts on claims, feel-check recorded:

```bash
python3 scripts/check_gates.py -r /path/to/repo [--slug <slice>] [--no-tests] [--json]
```

Exit `0` = no mechanical defects, `1` = at least one, `2` = cannot run. Its output always ends by naming what it could not check: RED attribution, guard-kill correctness, brief and design sufficiency, seam fidelity, rendering truth, whether the vision was right, whether a recorded approval was genuine. Exit 0 is not a signature.

It reads five conventions from the slice ledger — `base:`, `test-command:`, a fenced `closed-files` block, a `feel-check:` line, and `evidence/<file>` references. See SKILL.md.

## Requirements

The skill assumes three companion skills, each of which it cites rather than restates:

- **test-driven-development** — the RED→GREEN→REFACTOR sequence
- **systematic-debugging** — root-cause investigation when a failure has no named cause
- **dogfood** — the walk through a running surface on the user's path

In Hermes these ship bundled. The first two are adapted from [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent; the third is a first-party Hermes skill by Teknium. Elsewhere, substitute your own equivalents — the seam is what matters, not the names.

## Provenance

Derived from a personal lead-worker workflow, rebuilt phase by phase with the gates made explicit and the delegation machinery kept out of the discipline.

## License

MIT — see [LICENSE](LICENSE).
