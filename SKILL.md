---
name: implementation-discipline
description: "Use for technical work: eight gated phases, no skips."
version: 2.0.0
author: sirEven (GitHub), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
compatibility: "agentskills.io format. Requires the companion skills test-driven-development, systematic-debugging and dogfood."
metadata:
  hermes:
    tags: [workflow, gates, phases, discipline, tdd]
    related_skills: [test-driven-development, systematic-debugging, dogfood]
---

# Implementation Discipline

A gate approves exactly one thing: entry into the next phase. It may also refuse and send the work back to an earlier phase — this is never silent. No gate greenlights more than the next phase, no phase opens early, no phase is skipped.

VISION → OUTWARD RESEARCH → INWARD RESEARCH → ARCHITECTURE → SPLIT → DISPATCH → VERIFICATION → INTEGRATION

## When to Use

Technical work by default: code, config or system state changes, anything that changes how a project behaves. Not questions, explanations, prose, notes, or one-off reads. Whether it is overkill is the user's call.

## Seam

Three companions, each loaded at its moment, none of them restated here:

- **`test-driven-development`** — the sequence: RED→GREEN→REFACTOR, one behaviour at a time, minimal code. Nothing in this skill relaxes it.
- **`systematic-debugging`** — the investigation whenever a failure has no named cause.
- **`dogfood`** — the walk through a running surface on the user's path, required before sign-off on anything a user touches.

## Ledger conventions

`check_gates.py` reads five things from `Implementation/<slug>/note.md`. Write them literally:

```
base: <commit the idea started from>
test-command: <exact command that runs the suite>
max-files: 5
max-lines: 400
```

`max-files` and `max-lines` are optional; when absent the checker uses 5 and 400, and a CLI flag overrides both.

```closed-files
path/to/a
path/to/b
```

```
feel-check: APPROVED — "<their words>" — <ISO timestamp>
```

and evidence as `evidence/<file>`.

**Composites** — a composite carries `id: composite-k3f9x2`; every idea it produced carries `id: idea-k3f9x2#<position>`. Six characters from `23456789abcdefghjkmnpqrstuvwxyz`, generated once, regenerated if the id already appears under `Implementation/`. The composite's ledger lists what it produced:

```
ideas (riskiest first):
  #1  auth-token-refresh        pending
  #2  session-store-migration   pending
```

## The mechanical half

`scripts/check_gates.py` sits beside the phases and checks only what a machine can check exactly: closed file list, the ceiling, red suite, skip and focus markers in the diff, scratch residue, a gate under every phase present, evidence integrity, receipts on claims, feel-check recorded. Run it before claiming any gate; unconditionally at VERIFICATION and INTEGRATION.

Its NOT CHECKED footer names what stays mine — RED attribution, guard-kill correctness, brief and design sufficiency, seam fidelity, rendering truth, whether the vision was right, whether a recorded approval was genuine. Exit 0 is the absence of mechanical defects, never a signature.

## Standing rules — every phase

- **No red tests. Ever.** Not a failure you believe is unrelated to the change, not one that was red before you arrived, not one that is "expected in this environment", not a skip, not an expected-failure annotation, not a disabled test. A red test is a defect in the repository until it is green. It blocks every gate; fixing it becomes work in this idea or the next, never a note that says "known issue".
- Every claim carries a receipt: `file:line`, command output, or URL with version and date.
- Every claim is labelled measured or assumed.
- Self-reports — a worker's, or my own from an earlier turn — are claims, never evidence.
- A failure nobody can explain is handed to `systematic-debugging`; no fix ships until the cause is named. A guessed patch that happens to go green is a red test with better manners.
- Anything that changes the agreed plan — new behaviour, an unrequested refactor, a "better shape" — is a renegotiation with the user before it happens, presented as a measured fact with its receipt. Never a silent substitution, never a menu in place of a decided question.

## 1. VISION

**Triage** — one line: what I read the idea as, that the pipeline is opening, and the vision target. User confirms, corrects the target, or declines. Declined → recorded as "pipeline declined", work proceeds directly, no gate, no re-litigation.

**Rubberduck** — one question at a time, each waiting for its answer before the next. I open with my best draft of the vision from evidence, assumptions labelled, and question only what is genuinely uncertain. The loop ends when:

- one clean restatement, in my own words, carries no hedging
- nothing in it is unresolved — every open question is answered, or accepted by you as a risk
- nothing in it is mine to invent: every line traces to something you said, or to evidence with a receipt
- I can name what would make it wrong

**Produces** — a ledger in the repo the work touches, at `Implementation/<slug>/`: `note.md`, opening with the vision as I restated it and you confirmed it, and `evidence/` for captures and baseline runs, each named by what it proves. Later phases append to the same ledger.

**Amendments** — a vision amended after an OUTWARD return is edited in place, and the finding that forced the return is recorded in OUTWARD RESEARCH. A second VISION block is never legal; git holds the trail.

**Gate** — unambiguous approval in whatever form the user chooses: a plain yes, an edit to the note, an amendment spoken in the same breath. Silence, timeout or a polite non-answer is not approval → re-ask, no cap. Ambiguity test: if acting on it needs "did you mean…", it wasn't a gate. Passing it admits OUTWARD RESEARCH only.

## 2. OUTWARD RESEARCH

**Purpose** — compare the vision against everything that already exists in the world, before any code is mapped or designed.

**Produces**

- per element of the vision: what already does this — libraries, products, services, papers, specs — and what that means for us
- pivots: what would make the idea fundamentally different or better — a different data model, a managed service, conforming to an existing standard, dropping a requirement — with the reason each was taken or rejected
- prior art: candidate solutions with licence, maturity, maintenance state, cost, and why we would or would not adopt each
- claims that this is impossible or has never been done: recorded as inputs, never as rulings
- practice: spec, RFC or vendor guidance first; a source beats an article, an article beats an opinion

**Rules**

- The VISION is the propellant. Questions derive from its elements and from nothing else.
- No feasibility judgement about our code. Whether we can build it is INWARD RESEARCH's answer, on our own evidence.
- Outside pessimism is recorded, never obeyed. A source that says "this cannot be done" has not read our repository.
- Read-only.
- Stop when every element of the vision has been compared and every open question carries a source, or an explicit "nothing exists — we decide".

**Gate** — two exits, and only two:

- **clear** → INWARD RESEARCH opens.
- **return to VISION** → the vision is amended and re-approved by the user.

The return loop is unbounded: it runs until the vision is perfect, however many passes that takes. Each return names the finding that forced it — a loop that changes nothing means the fence is wrong, not that the vision is finished.

## 3. INWARD RESEARCH

**Purpose** — establish what exists inside the project and around it: the code, our dependencies, the contracts, the baseline. ARCHITECTURE should not have to guess at any of it.

**Produces**

- files to change: path, contents, exact anchor line, each read in full
- entry paths to the touched code, each traced to where it leaves the codebase
- dependents: callers, importers, readers of the shape being changed
- dependencies we already run: the source of the version in use — not the development branch, not the docs site · open issues, PRs, changelog and migration notes; whether this is already being built, or deliberately rejected upstream
- existing tests over the area, plus the command that runs them
- contracts: real payloads and formats, with a captured sample
- baseline: current suite result; a reproduction for defect work
- what remains a decision, each with the design question it blocks

**Rules**

- Read-only. Repairs found anywhere are reported, never applied.
- Every finding ties to a decision it enables, or it is trivia.
- Questions come from the VISION and the map; one that blocks no design decision is trivia.
- Stop when every open question carries a source, or an explicit "no answer exists — this is a decision".

**Gate** — spot-check: two claims picked at random, re-verified from disk. Sufficiency: ARCHITECTURE can answer its design questions from this map alone, without re-reading source. A wrong claim reopens the phase.

## 4. ARCHITECTURE

**Purpose** — turn vision plus evidence into a function-level design, precise enough that SPLIT can cut it by file and DISPATCH can brief without re-deciding anything.

**Produces, in this order**

1. **Decomposition** — an estimate against the ceiling: 5 files and 400 changed lines by default, set per idea in the ledger. Under it, design proceeds. Over it, two options are priced and the gate chooses between them:

   - **composite** — the idea decomposes into a composite. Its ledger lists the ideas it produced, riskiest first, one line each with a status, and pins the seams between them. Each of those is an idea like any other, opening at VISION in inheritance mode with the composite's stamp in its header. The composite closes when its last idea closes.
   - **raise** — the idea runs whole at a ceiling of the estimate plus a fifth, rounded up to a whole file and to ten lines. No upper bound; the gate carries the decision.

   Either way the ledger records the estimate and what was granted.
2. **Seams** — the interfaces between ideas, pinned. Changing one later is a renegotiation, never an idea's private choice.
3. **Design of the current idea only** — file list, one line per file on what changes · interfaces: signatures, inputs and outputs, error contracts, data shapes crossing module boundaries · abstractions and one-way dependency direction · extraction: a file other work also depends on gets its domain pulled into its own module as part of this design, a byproduct of the idea, never a standalone refactor cycle · build order · test seams, where the guards will live · excluded neighbours: near siblings that must not be touched, listed only if they exist · size in files and lines.
4. **Traceability, both directions** — every element of the vision maps to at least one design element; every design element names the outcome it serves or the necessity it satisfies.

**Rules**

- Lead alone. Design is not delegated; workers receive pinned interfaces, they never invent them.
- No implementation inside a design: signatures and contracts, no bodies.
- Design against INWARD RESEARCH receipts. An assumption not in evidence sends the phase back, not forward.
- Every abstraction pays for itself. No speculative generality, no standalone refactor.

**Gate** — **coverage:** every element of the vision mapped, every file in the map either in the file list or explicitly untouched. **Sufficiency:** SPLIT can cut disjoint file sets from this alone, and DISPATCH can brief with no design decision left open. **Decomposition:** when an idea decomposes, the composite is presented once, since riskiest-first changes what ships when — that presentation is the gate. **Triggers:** irreversible action, new dependency or licence, security surface, divergence from evidence or vision → mandatory user gate before SPLIT. No trigger fired → self-gated, proceed.

## 5. SPLIT

**Purpose** — cut the current idea into tasks that can be executed and verified without interfering with each other.

**Produces**

- **task list** — per task: closed file set · the design elements it implements · interfaces consumed and provided, as pinned · exit condition, meaning the tests that encode it
- **relations** — disjoint tasks run at once; any pair sharing a file is sequenced explicitly, with the order written down
- **merge order**, and where the pinned interfaces get checked after merge
- **shared files** — a task that must touch one waits for the extraction designed in ARCHITECTURE, or the idea goes back there; nothing is extracted privately inside a task

**Rules**

- Disjoint by construction. The closed file list is computed per task; a shared file forces sequencing or extraction.
- At most three tasks in flight. Concurrency beyond that costs more verification than it returns.
- A task owns its code and its tests. Separating tests from the implementation is how tests come to describe imagined code instead of required behaviour.
- A task over the ceiling means the idea was mis-sized → back to ARCHITECTURE.

**Gate** — **disjointness:** the task file sets compared mechanically, intersection empty. **Coverage:** the union of task sets equals the idea's file list, nothing dropped. **Briefability:** each task executable from a self-contained brief, by a worker with no access to the other tasks' context. **Ordering:** every non-disjoint pair sequenced in writing. Technical — no user gate.

## 6. DISPATCH

**Purpose** — turn each task into a brief a worker can execute without asking anything, then send it and hold the line while it runs.

**Brief anatomy** — the task's scope in one line and its exit condition · closed file list with `file:line` anchors verified in INWARD RESEARCH · pinned interfaces as verbatim signature text, never a description of them · the tests to write, stated as behaviour · excluded neighbours · the project's test command · read limit: the closed file list and its imports, nothing exploratory · the deviation rule verbatim · done definition: the exact state and outputs to return.

**Test briefs** — stub every network path the unit touches: on setup, on interaction, and on the error path. Error-path tests abort before any call, so a raising stub proves the request is never reached. Assert the resulting state, not the absence of an exception. An unstubbed path is how a guard-kill later passes for the wrong reason.

**Rules**

- Design decisions are never delegated. A worker that needs one stops and reports.
- One brief per task; no brief spans two tasks.
- Workers report blockers to the lead, never to the user, and never re-scope.
- A blocked or partial return belongs to DISPATCH: re-brief it, or send it back to ARCHITECTURE if the design is at fault. VERIFICATION only ever sees work claimed complete.

**Solo mode** — no workers: the brief is the task's exit condition, and the tasks run in the written order. Same discipline, no paperwork.

**Gate** — each brief read as a stranger would, against a mechanical checklist: closed file list · interfaces verbatim · test command · read limit · deviation rule · done definition. One brief per task; nothing dispatched until its sequenced predecessor has integrated. Technical — no user gate.

## 7. VERIFICATION

**Purpose** — establish by my own execution that the delivered task does what the design says, and that its tests would catch it if it didn't.

**Actions, per delivered unit**

- read the diff file by file, all of it
- run the full suite, never the focused files the worker was told to run
- **guard-kill** — disable one guard the tests claim to cover → demand RED for that reason → restore → GREEN. Kill results must be attributable: a RED from broken stubs or a real socket proves nothing
- **fixture check** — any parser or renderer of third-party output carries a real-payload test; measurement assertions check shape, and have been observed failing
- **dogfood, mandatory on any user-facing surface** — load the `dogfood` skill and walk the delivered work's path the way a user would, with its evidence and reporting discipline; for anything that renders, measure the output rather than merely confirming it exists
- **user-reported defects** — the report is the specification; reproduce it before theorising, then hand the investigation to `systematic-debugging`. A failing test on the user's path is the default reproduction; where no test seam reaches the symptom, the tightest available repro is acceptable only if the ledger names it and names the gap. Where the symptom is a quantity — how much, how many, how long, where — measure the value, not its presence
- **scratch sweep** — untracked residue is suspect until proven a dependency

**Rules**

- A flake is a bug with an unproven cause.
- A repair made directly is legitimate only when it is smaller than the brief that would describe it — a typo, a rename, a missing import. Still RED-first, still recorded in the ledger with its own verification rerun. Anything larger goes back, because a silent repair hides a broken brief.
- Nothing is signed because the suite is green. It is signed because the guard died and the path ran.

**Gate** — every action above performed, with receipts in the ledger: the commands, their output, the measurements, the guard that was killed and what it produced. An action not done is written down as not done, never implied by silence. Technical — no user gate.

## 8. INTEGRATION

**Purpose** — fold the verified task into the codebase so the system is whole and better than before, then close the ledger entry.

**Actions**

- merge in the written order, running the full suite after each merge — a green task can still break the codebase on contact
- check the pinned seams: every interface as designed, no task quietly widened one. A seam that moved is a design amendment recorded as such, never a merge detail
- run it, let the user use it, take the feel-check
- commit only after the feel-check passes, with a message naming the idea and the part of the vision it serves
- ledger entry: what shipped · what was proven · what was deferred · the gate receipts
- **close-out**, when this was the last task of the last idea and no idea of a composite is left pending: every element of the vision traced to shipped work, the system exercised end to end, seams checked against what was pinned

**Branches** — a concurrency tool, not a structure. One checkout by default, tasks committing in the written order. A branch or a second checkout exists only while two tasks are in flight, or when a change must be revertable as a unit; it is merged or discarded before the idea's feel-check, never left open.

**Rules**

- Never anything over a red or skipped test — see standing rules.
- Merge is not where anything gets fixed. A defect found here goes back a phase.
- Nothing is done until the feel-check answers.

**Gate** — the user's feel-check, unambiguous, same standard as VISION: silence is not consent. Passing it closes the task and writes the commit. If the idea decomposed into a composite, its next idea opens at VISION in inheritance mode.
