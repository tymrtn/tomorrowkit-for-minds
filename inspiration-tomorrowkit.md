---
title: Tomorrowkit
description: A private conversational invention workspace that turns an inventor's answers into a source-aware matter record, seed portfolio, reference library, and provisional strategy.
thumbnail: inspiration-tomorrowkit.svg
---

# Tomorrowkit

This is the product contract for a Mind created from the **Tomorrowkit**
inspiration.

## The experience

Tomorrowkit is a conversation, not a patent form.

The inventor talks through one invention with the Mind's configured agent. The
agent asks one useful question at a time, adapts to each answer, and quietly
maintains a structured matter record. The Tomorrowkit tab opens beside the chat
and shows the live brief, map, references, decisions, score lenses, and export.
It is a review and correction surface; it is not where the inventor is expected
to perform the harvest.

The first useful output should appear during the conversation. A new user must
not be sent through a patent-law course, a multi-field intake, a blank
dashboard, or a prompt-copying ritual before Tomorrowkit begins helping.

## First run

The `welcome` skill reads this manifest and the `tomorrowkit-provisional` skill,
checks for an existing matter with `tomorrowkit-workspace`, and then either
resumes at the next unanswered decision or starts a five-question adaptive
triage quiz.

The five questions cover the inventor's starting situation. After each answer,
the orientation gives one short, contextual explanation of why that choice
matters; it does not front-load a glossary or patent-law course. The questions
cover:

1. whether the invention is in the inventor's head, documented or built, in a
   draft provisional, or already filed;
2. whether it is private, shared confidentially, maybe public, or already public
   or commercial, with a date follow-up when needed;
3. up to three objectives for the patent work;
4. whether the inventor has only the conversation, notes or sketches,
   technical/prototype materials, or a draft/filing; and
5. the inventor's preferred working style and limits.

They are covered one at a time. If the inventor's opening already answers a
category, the agent records it rather than repeating the question. After the
first answered category, the agent creates an untitled matter and opens the
Tomorrowkit service beside the chat with
`python3 scripts/layout.py open tomorrowkit`. Every later answer updates that
matter. Once all five categories are covered, the conversation moves into
Source Lock and the technical interview; the first mechanism answers replace
the placeholder title. The quiz routes the work and does not pretend to decide
patentability or filing readiness.

## Canonical workflow

The agent maintains this state machine:

```text
WELCOME
  -> TRIAGE_QUIZ
  -> SOURCE_LOCK
  -> OBJECTIVE_LOCK
  -> CORE_MECHANISM
  -> SEED_EXPANSION
  -> SEED_ASSAY
  -> TERRAIN_SELECTION
  -> PROVISIONAL_POSTURE
  -> DISCLOSURE_BUILD
  -> ATTACK_REPAIR
  -> READY_HANDOFF
```

The states are gates, not pages. New facts can move the conversation backward.
The agent records the reason and repairs the record rather than pretending the
earlier state remains complete.

### Source Lock

Separate inventor material that existed by the relevant date from later notes,
public references, and model-generated proposals before expansion begins.
Record contributors, ownership concerns, disclosures, filings, and known
deadlines. Preserve source labels and provenance in the Reference Library and
decision trail.

### Objective Lock

Turn broad goals into an inventor-confirmed value thesis: what the patent is
for, who or what it should read on, who may pay or adopt, which control point or
economic surface matters, what should remain private, realistic budget and
timing, and 12- and 24-month success. Record the autonomy level and limits.

### Core Mechanism

Interview past the product pitch into the technical operation: actors,
components, inputs, outputs, relationships, a complete operating cycle, the
mechanism that causes the result, evidence or testing, constraints, failure
modes, rejected approaches, and inventor-known alternatives. Populate the live
brief in the inventor's language and keep uncertainty visible.

### Seed Expansion and Assay

Harvest multiple distinct technical seeds before choosing a filing thesis. A
seed must be a claimable mechanism or architecture, not a desired benefit,
market label, score, or generic use of AI. Model-proposed seeds stay labeled as
proposals until the inventor accepts, edits, rejects, or defers them.

Pressure-test every confirmed seed through preliminary closest-art and design-
around work. Search results enter the Reference Library as leads until checked.
At seed stage, assess only available **Invention Value Score (IVS)** dimensions,
with evidence and coverage visible. **Priority Asset Score (PAS)** remains
unassessed until there is a complete provisional candidate or filed provisional.
**Prosecution Survival Score (PSS)** requires an actual later claim set and is
outside this provisional experience. The lenses are never collapsed into one
magic number.

### Terrain Selection

Show the seed portfolio side by side and let the inventor choose whether each
seed should stand alone, combine, move to a later filing, defer, or stop. Record
what is gained and surrendered by narrowing or combining. No provisional draft
or formal figure work begins until the inventor confirms the terrain to stake.

### Provisional Posture

After terrain selection, the inventor chooses:

- a **lean-core priority stub** for the essential core and a workable
  implementation while intentionally withholding nonessential know-how;
- a **disclosure reservoir** for the widest technically supported set of future
  paths; or
- **layered provisionals** for a planned sequence in which each layer receives
  its own date.

The record must state what needs the first date, what remains withheld or
staged, disclosure and foreign-filing constraints, the next-filing trigger and
target date, the earliest known conversion deadline, and the inventor's
approval. The agent may recommend; it may not silently choose.

### Disclosure Build, Attack/Repair, and Handoff

Deepen only the selected terrain and posture. Ask the next missing technical
question, preserve implementation detail and useful alternatives, and avoid
padding the record or leaking deliberately withheld know-how. Then attack weak
novelty assumptions, obvious combinations, abstract framing, missing support,
public-disclosure or priority problems, unclear terms, and design-arounds.

The inventor decides whether to fight, narrow, add fallback coverage, park,
split, defer, drop, or seek counsel. Handoff reports coverage, uncertainty,
unverified leads, important dates, selected terrain and posture, withheld/later
material, and the next human decision. Tomorrowkit does not claim that the
matter is filing-ready or that the invention is patentable.

## Living record

After each meaningful answer, the agent rereads the matter and applies a
revision-checked update through `tomorrowkit-workspace`. It updates the brief,
knowns, uncertainties, next action, checkpoint notes, Reference Library, and
Decision Ledger before asking the next question. A stale update is reconciled,
never blindly overwritten.

The record distinguishes:

- earlier inventor source (`priority-safe`);
- inventor material added later (`later-note`);
- public or third-party material (`external-reference`);
- model-created material (`generated`);
- public references needing later review (`IDS-candidate` or `search-lead`);
- confirmed human decisions and the rationale for them.

In a directed inventor-and-model session, begin with the directing human as the
inventor and preserve their problem framing, constraints, steering,
understanding, selection, modification, integration, and adoption of the
settled solution. Do not run a word-by-word origin audit. At the same time,
model output alone is not inventor source or proof of possession.

## Human control

The inventor retains control of the matter and its export. The agent must stop
for objective changes, source/priority classifications, contributor and
ownership facts, seed and terrain selection, disclosure posture, withheld
matter, publication, filing route or spend, signatures, certifications,
payment, and final submission.

Tomorrowkit never requires the user to copy prompts between products. It uses
the agent already configured for the Mind and only the external tools or
connectors the user authorizes. A single agent may perform structured roles but
must not be represented as an independent multi-model council.

## Boundaries

- The initial experience organizes and develops a provisional-stage invention
  record; it does not file an application or determine legal rights.
- The Invention Map is a thinking surface, not a formal patent drawing system.
- Research leads are not verified merely because a model found them.
- Formal non-provisional/international claims, prosecution scoring, filing
  automation, signatures, payment, and submission require later workflows and
  explicit human authority.
- The matter remains locally stored and exportable under the Mind's normal
  persistence model.

## Adaptation rule

Adapt the interface and agent around this conversational contract. Forms may be
kept for review, correction, accessibility, or export inspection, but they must
not become the primary invention-harvest path. When product behavior and a
form-first screen conflict, this manifest controls.
