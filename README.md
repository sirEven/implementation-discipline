# Implementation Discipline

A skill for coding agents. Eight phases, each with a gate that admits entry into the next phase and nothing more.

```
VISION → OUTWARD RESEARCH → INWARD RESEARCH → ARCHITECT → SPLIT → DISPATCH → VERIFY → INTEGRATE
```

| phase | output |
|---|---|
| VISION | agreed destination: problem, who it serves, observable outcome, non-goals, constraints, unknowns |
| OUTWARD RESEARCH | the world against the vision: what already exists, pivots worth taking, claims that it cannot be done — may return to VISION as often as it takes |
| INWARD RESEARCH | the project: files, entry paths, dependencies in use, contracts, baseline |
| ARCHITECT | function-level design, and a slice plan when the work exceeds the cycle ceiling |
| SPLIT | lanes with disjoint file sets, sequenced where they touch the same file |
| DISPATCH | one self-contained brief per lane |
| VERIFY | proof by execution: the diff read, the suite run, a guard killed, the user's path walked |
| INTEGRATE | merge in written order, seam check, feel-check, commit |

## Install

Any agent that reads the [agentskills.io](https://agentskills.io/specification) `SKILL.md` format: copy this directory into its skills folder. Frontmatter keys specific to Hermes sit under `metadata.hermes` and are ignored elsewhere.

## Scripts

`scripts/check_gates.py` — checks the mechanical part of the gates against a slice ledger.

```bash
python3 scripts/check_gates.py --help
```

## Companion skills

The skill cites three and restates none of them: `test-driven-development`, `systematic-debugging`, `dogfood`. Where they are not installed, supply equivalents.

## License

MIT — see [LICENSE](LICENSE).
