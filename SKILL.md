---
name: implementation-discipline
description: "Use for technical work: seven gated phases, no skips."
version: 1.0.0
author: sirEven (GitHub), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
compatibility: "Hermes Agent (agentskills.io format). Requires the skills test-driven-development, systematic-debugging and dogfood."
metadata:
  hermes:
    tags: [workflow, gates, phases, discipline, tdd]
    related_skills: [test-driven-development, systematic-debugging, dogfood]
---

# Implementation Discipline

A gate approves exactly one thing: entry into the next phase. No gate greenlights an undertaking, no phase opens early, no phase is skipped silently.

VISION → RESEARCH → ARCHITECT → SPLIT → DISPATCH → VERIFY → INTEGRATE

## When to Use

Technical work by default: code, config or system state changes, anything that changes how a project behaves. Not questions, explanations, prose, notes, or one-off reads. Whether it is overkill is the user's call, at triage, in one word — never a silent downgrade.

## Seam

Three companions, each loaded at its moment, none of them restated here:

- **`test-driven-development`** — the sequence: RED→GREEN→REFACTOR, one behaviour at a time, minimal code. Nothing in this skill relaxes it.
- **`systematic-debugging`** — the investigation whenever a failure has no named cause.
- **`dogfood`** — the walk through a running surface on the user's path, required before sign-off on anything a user touches.

## Ledger conventions

`check_gates.py` reads five things from `Implementation/<slug>/note.md`. Write them literally:

```
base: <commit the slice started from>
test-command: <exact command that runs the suite>
```

```closed-files
path/to/a
path/to/b
```

```
feel-check: APPROVED — "<their words>" — <ISO timestamp>
```

and evidence as `evidence/<file>`.

## The mechanical half

`scripts/check_gates.py` sits beside the phases and checks only what a machine can check exactly: closed file list, cycle ceiling, red suite, skip and focus markers in the diff, scratch residue, a gate under every phase present, evidence integrity, receipts on claims, feel-check recorded. Run it before claiming any gate; unconditionally at VERIFY and INTEGRATE.

Its NOT CHECKED footer names what stays mine — RED attribution, guard-kill correctness, brief and design sufficiency, seam fidelity, rendering truth, whether the vision was right, whether a recorded approval was genuine. Exit 0 is the absence of mechanical defects, never a signature.

## Standing rules — every phase

- **No red tests. Ever.** Not a failure you believe is unrelated to the change, not one that was red before you arrived, not one that is "expected in this environment", not a skip, not an expected-failure annotation, not a disabled test. A red test is a defect in the repository until it is green. It blocks every gate; fixing it becomes work in this slice or the next, never a note that says "known issue".
- Every claim carries a receipt: `file:line`, command output, or URL with version and date.
- Every claim is labelled measured or assumed.
- Self-reports — a worker's, or my own from an earlier turn — are claims, never evidence.
- A failure nobody can explain is handed to `systematic-debugging`; no fix ships until the cause is named. A guessed patch that happens to go green is a red test with better manners.
- Anything that changes the agreed plan — new behaviour, an unrequested refactor, a "better shape" — is a renegotiation with the user before it happens, presented as a measured fact with its receipt. Never a silent substitution, never a menu in place of a decided question.

## 1. VISION

**Triage** — one line: what I read the task as, that the pipeline is opening, and the vision target. User confirms, corrects the target, or declines. Declined → recorded as "pipeline declined", work proceeds directly, no gate, no re-litigation.

**Rubberduck** — one question at a time, each waiting for its answer before the next. I open with my best draft of the vision from evidence, assumptions labelled, and question only what is genuinely uncertain. The loop ends when:

- every field is filled
- no unknown is unowned — answered, or accepted as a risk by the user
- one clean restatement carries no hedging
- I can name what would make the vision wrong

**Produces** — a ledger in the repo the work touches, at `Implementation/<slug>/`: `note.md` — problem · who and situation · observable outcome · non-goals · hard constraints · unknowns, each marked answered or accepted-risk — and `evidence/` for captured payloads, screenshots, logs and baseline runs, each named by what it proves. No quality bar, no abandon condition. Later phases append to the same ledger.

**Gate** — unambiguous approval in whatever form the user chooses: a plain yes, an edit to the note, an amendment spoken in the same breath. Silence, timeout or a polite non-answer is not approval → re-ask, no cap. Ambiguity test: if acting on it needs "did you mean…", it wasn't a gate. Passing it admits RESEARCH only.

## 2. RESEARCH

**Purpose** — establish what exists before anything is designed: what our code does, what our dependencies do, what the field has already solved. ARCHITECT should not have to guess at any of it.

**Inward — the project, code truth**

- files to change: path, contents, exact anchor line, each read in full
- entry paths to the touched code, each traced to where it leaves the codebase
- dependents: callers, importers, readers of the shape being changed
- dependencies we already run: the source of the version in use — not the development branch, not the docs site · open issues, PRs, changelog and migration notes; whether this is already being built, or deliberately rejected upstream
- existing tests over the area, plus the command that runs them
- contracts: real payloads and formats, with a captured sample
- baseline: current suite result; a reproduction for defect work

**Outward — the world, existing resources**

- the problem solved elsewhere: search outside our stack — libraries, products, services, papers, specs — for something that already does this, before anything is designed
- first principles: what would make the undertaking fundamentally different or better — a different data model, a managed service, conforming to an existing standard, dropping a requirement. Record the pivot and the reason it was taken or rejected; one that changes the vision goes back to VISION
- prior art: candidate solutions with licence, maturity, maintenance state, cost, and why we would or would not adopt each
- practice: spec, RFC or vendor guidance first; a source beats an article, an article beats an opinion

**Rules**

- Read-only. Repairs found anywhere are reported, never applied.
- Every finding ties to a decision it enables, or it is trivia.
- Questions come from the VISION and the map. RESEARCH may add one only by naming the design decision it blocks.
- Stop when every open question carries a source, or an explicit "no answer exists — this is a decision".

**Produces** — appended to the ledger: the map, plus four lists — what we now know · what we will not build because it exists · pivots considered, with the reason each was taken or rejected · what remains a decision.

**Gate** — spot-check: two claims picked at random, re-verified at their source, disk for internal and the cited artifact for external. Sufficiency test: ARCHITECT can answer its design questions from this note alone, without a browser and without re-reading source. Unanswered external questions appear as decisions, never as silence. A wrong claim reopens the phase.

## 3. ARCHITECT

**Purpose** — turn vision plus evidence into a function-level design, precise enough that SPLIT can cut it by file and DISPATCH can brief without re-deciding anything.

**Produces, in this order**

1. **Decomposition** — an estimate against the ceiling (about 5 files, 400 changed lines). Over it, the undertaking is cut into slices: each a full pipeline run, each leaving the system working, ordered riskiest first, with the seams between them pinned. Under it, the verdict is "single cycle".
2. **Seams** — the interfaces between slices, pinned. Changing one later is a renegotiation, never a slice's private choice.
3. **Design of the current slice only** — file list, one line per file on what changes · interfaces: signatures, inputs and outputs, error contracts, data shapes crossing module boundaries · abstractions and one-way dependency direction · extraction: a file other work also depends on gets its domain pulled into its own module as part of this design, a byproduct of the slice, never a standalone refactor cycle · build order · test seams, where the guards will live · excluded neighbours: near siblings that must not be touched, listed only if they exist · size in files and lines.
4. **Traceability, both directions** — every vision outcome maps to at least one design element; every design element names the outcome it serves or the necessity it satisfies.

**Rules**

- Lead alone. Design is not delegated; workers receive pinned interfaces, they never invent them.
- No implementation inside a design: signatures and contracts, no bodies.
- Design against RESEARCH receipts. An assumption not in evidence sends the phase back, not forward.
- Every abstraction pays for itself. No speculative generality, no standalone refactor.

**Gate** — **coverage:** every outcome mapped, every file in the map either in the file list or explicitly untouched. **Sufficiency:** SPLIT can cut disjoint file sets from this alone, and DISPATCH can brief with no design decision left open. **Decomposition:** a slice plan is presented once, since riskiest-first changes what ships when — that presentation is the gate. **Triggers:** irreversible action, new dependency or licence, security surface, divergence from evidence or vision → mandatory user gate before SPLIT. No trigger fired → self-gated, proceed.

## 4. SPLIT

**Purpose** — cut the current slice into lanes that can be executed and verified without interfering with each other.

**Produces**

- **lane list** — per lane: closed file set · the design elements it implements · interfaces consumed and provided, as pinned · exit condition, meaning the tests that encode it
- **relations** — disjoint lanes run at once; any pair sharing a file is sequenced explicitly, with the order written down
- **merge order**, and where the pinned interfaces get checked after merge
- **shared files** — a lane that must touch one waits for the extraction designed in ARCHITECT, or the slice goes back there; nothing is extracted privately inside a lane

**Rules**

- Disjoint by construction. The closed file list is computed per lane; a shared file forces sequencing or extraction.
- At most three lanes in flight. Concurrency beyond that costs more verification than it returns.
- A lane owns its code and its tests. Splitting tests away from the implementation is how tests come to describe imagined code instead of required behaviour.
- A lane over the cycle ceiling means the slice was mis-sized → back to ARCHITECT.

**Gate** — **disjointness:** the lane file sets compared mechanically, intersection empty. **Coverage:** the union of lane sets equals the slice's file list, nothing dropped. **Briefability:** each lane executable from a self-contained brief, by a worker with no access to the other lanes' context. **Ordering:** every non-disjoint pair sequenced in writing. Technical — no user gate.

## 5. DISPATCH

**Purpose** — turn each lane into a brief a worker can execute without asking anything, then send it and hold the line while it runs.

**Brief anatomy** — the lane's scope in one line and its exit condition · closed file list with `file:line` anchors verified in RESEARCH · pinned interfaces as verbatim signature text, never a description of them · the tests to write, stated as behaviour · excluded neighbours · the project's test command · read limit: the closed file list and its imports, nothing exploratory · the deviation rule verbatim · done definition: the exact state and outputs to return.

**Test briefs** — stub every network path the unit touches: on setup, on interaction, and on the error path. Error-path tests abort before any call, so a raising stub proves the request is never reached. Assert the resulting state, not the absence of an exception. An unstubbed path is how a guard-kill later passes for the wrong reason.

**Rules**

- Design decisions are never delegated. A worker that needs one stops and reports.
- One brief per lane; no brief spans two lanes.
- Workers report blockers to the lead, never to the user, and never re-scope.
- A blocked or partial return belongs to DISPATCH: re-brief it, or send it back to ARCHITECT if the design is at fault. VERIFY only ever sees work claimed complete.

**Solo mode** — no workers: the brief is the lane's exit condition, and the lanes run in the written order. Same discipline, no paperwork.

**Gate** — each brief read as a stranger would, against a mechanical checklist: closed file list · interfaces verbatim · test command · read limit · deviation rule · done definition. One brief per lane; nothing dispatched until its sequenced predecessor has integrated. Technical — no user gate.

## 6. VERIFY

**Purpose** — establish by my own execution that the delivered lane does what the design says, and that its tests would catch it if it didn't.

**Actions, per delivered unit**

- read the diff file by file, all of it
- run the full suite, never the focused files the worker was told to run
- **guard-kill** — disable one guard the tests claim to cover → demand RED for that reason → restore → GREEN. Kill results must be attributable: a RED from broken stubs or a real socket proves nothing
- **fixture check** — any parser or renderer of third-party output carries a real-payload test; measurement assertions check shape, and have been observed failing
- **dogfood, mandatory on any user-facing surface** — load the `dogfood` skill and walk the lane's path the way a user would, with its evidence and reporting discipline; for anything that renders, measure the output rather than merely confirming it exists
- **user-reported defects** — the report is the specification; reproduce it before theorising, then hand the investigation to `systematic-debugging`. A failing test on the user's path is the default reproduction; where no test seam reaches the symptom, the tightest available repro is acceptable only if the ledger names it and names the gap. Where the symptom is a quantity — how much, how many, how long, where — measure the value, not its presence
- **scratch sweep** — untracked residue is suspect until proven a dependency

**Rules**

- A flake is a bug with an unproven cause.
- A repair made directly is legitimate only when it is smaller than the brief that would describe it — a typo, a rename, a missing import. Still RED-first, still recorded in the ledger with its own verification rerun. Anything larger goes back, because a silent repair hides a broken brief.
- Nothing is signed because the suite is green. It is signed because the guard died and the path ran.

**Gate** — every action above performed, with receipts in the ledger: the commands, their output, the measurements, the guard that was killed and what it produced. An action not done is written down as not done, never implied by silence. Technical — no user gate.

## 7. INTEGRATE

**Purpose** — fold the verified lane into the codebase so the system is whole and better than before, then close the ledger entry.

**Actions**

- merge in the written order, running the full suite after each merge — a green lane can still break the codebase on contact
- check the pinned seams: every interface as designed, no lane quietly widened one. A seam that moved is a design amendment recorded as such, never a merge detail
- run it, let the user use it, take the feel-check
- commit only after the feel-check passes, with a message naming the slice and the vision outcome it serves
- ledger entry: what shipped · what was proven · what was deferred · the gate receipts
- **programme close**, when this was the final slice: every vision outcome traced to a shipped slice, the system exercised end to end, seams checked against what was pinned

**Branches** — a concurrency tool, not a structure. One checkout by default, lanes committing in the written order. A branch or a second checkout exists only while two lanes are in flight, or when a change must be revertable as a unit; it is merged or discarded before the slice's feel-check, never left open.

**Rules**

- Never anything over a red or skipped test — see standing rules.
- Merge is not where anything gets fixed. A defect found here goes back a phase.
- Nothing is done until the feel-check answers.

**Gate** — the user's feel-check, unambiguous, same standard as VISION: silence is not consent. Passing it closes the cycle and writes the commit. If slices remain, the next opens at VISION in inheritance mode.
