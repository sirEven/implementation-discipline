# Implementation Discipline

A skill for coding agents. Eight phases, each with a gate that admits entry into the next phase and nothing more.

```
VISION → OUTWARD RESEARCH → INWARD RESEARCH → ARCHITECTURE → SPLIT → DISPATCH → VERIFICATION → INTEGRATION
```

| phase | output |
|---|---|
| VISION | the vision, restated by the agent and confirmed by you |
| OUTWARD RESEARCH | the world against the vision: what already exists, pivots worth taking, claims that it cannot be done — may return to VISION as often as it takes |
| INWARD RESEARCH | the project: files, entry paths, dependencies in use, contracts, baseline |
| ARCHITECTURE | function-level design, and — when the idea exceeds the ceiling — either a composite or a raised ceiling |
| SPLIT | tasks with disjoint file sets, sequenced where they touch the same file |
| DISPATCH | one self-contained brief per task |
| VERIFICATION | proof by execution: the diff read, the suite run, a guard killed, the user's path walked |
| INTEGRATION | land in written order, seam check, feel-check, commit |

## Terms

**Idea** — one full run of the eight phases: a piece of intent small enough to design, build and verify in a single pass.

**Task** — a parallel piece of an idea: a disjoint set of files handed to one self-contained brief. Tasks never cross ideas.

**Composite** — what an over-sized idea becomes when it decomposes instead of raising its ceiling: a record listing the ideas it produced, riskiest first, with the seams between them pinned. It runs no phases and closes when its last idea closes.

## Install

Any agent that reads the [agentskills.io](https://agentskills.io/specification) `SKILL.md` format: copy this directory into its skills folder. Host-specific frontmatter sits under `metadata.hermes` and is ignored by tools that don't read it.

## Scripts

`scripts/check_gates.py` — checks the mechanical part of the gates against an idea's ledger.

```bash
python3 scripts/check_gates.py --help
```

## Configuration

The checker reads these from the idea's ledger:

| key | required | default | override |
|---|---|---|---|
| `base` | yes | — | — |
| `test-command` | yes | — | — |
| `max-files` | no | 5 | `--max-files` |
| `max-lines` | no | 400 | `--max-lines` |

It also reads the fenced `closed-files` block and the `feel-check:` line; both are described in SKILL.md.

Two things that are not settings. The three-task limit is a rule of the pipeline, not a knob. And the ceiling is a trigger with teeth: the checker fails an idea that crosses it, which sends the work back to ARCHITECTURE — where it either decomposes into a composite or runs at a raised ceiling.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Stdlib only, no install step. Each test builds a throwaway git repository in a temporary directory, so nothing here depends on where the repo was cloned.

## Companion skills

The skill cites three and restates none of them: `test-driven-development`, `systematic-debugging`, `dogfood`. Where they are not installed, supply equivalents.

## License

MIT — see [LICENSE](LICENSE).
