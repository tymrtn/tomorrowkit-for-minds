# Tomorrowkit for Minds — Conversational Product Architecture

## Product decision

Tomorrowkit is an interactive invention-harvest conversation with a living
record beside it. The chat is the primary product surface. The web service is a
record viewer, visual thinking surface, correction layer, and export tool.

This supersedes the earlier form-first architecture. A long orientation page,
matter-creation form, blank brief, checkpoint administrator, or scorecard full
of empty fields is not the intended user journey. Those controls may remain as
secondary inspection and correction affordances, but the agent must create and
maintain the record through the conversation.

## Product promise

**Tell Tomorrowkit how the invention works. Watch the invention record take
shape.**

A solo inventor should be able to begin with an unpolished explanation, answer
one useful question at a time, and leave with:

- a source-aware invention brief;
- a concrete technical mechanism and representative implementation;
- multiple inventor-confirmed invention seeds before thesis selection;
- a living Reference Library with provenance and verification state;
- an inventor-approved objective profile and terrain declaration;
- an explicit provisional disclosure posture;
- a human decision trail, visible uncertainty, and next action; and
- a portable matter export.

## Surface model

Three pieces share one matter:

1. **Minds chat — primary surface.** The configured agent runs the adaptive
   interview, proposes alternatives, explains decisions in context, and asks
   one useful question per turn.
2. **Tomorrowkit tab — live sidecar.** It displays the brief, map, sources,
   decisions, score lenses, and export. It opens beside the chat with
   `python3 scripts/layout.py open tomorrowkit` after a matter is created or
   resumed.
3. **`tomorrowkit-workspace` — validated bridge.** The agent lists, creates,
   reads, and revision-checks record updates. The user never moves prompts or
   answers between surfaces.

The conversation and record are not two separate workflows. Each meaningful
answer changes the same matter the sidecar displays.

## First-run experience

### Resume before onboarding

On entry, the agent runs `tomorrowkit-workspace list`. If a matter exists, it
reads the current record, opens the Tomorrowkit tab beside chat, gives a compact
recap, and asks the next state-specific question. It does not restart the quiz
or ask the inventor to repeat information already in the matter.

### Five-question adaptive triage

If no matter exists, the agent asks exactly five setup questions, one at a
time:

1. Where does it stand: in the inventor's head, documented or built, in a draft
   provisional, or already filed?
2. Is it private, shared only confidentially, maybe public, or already public or
   commercial? If disclosure may have occurred, what and when?
3. What should the patent work accomplish? The inventor may select up to three
   objectives.
4. What source material exists: this conversation only, notes or sketches,
   technical/prototype materials, or a draft/filing?
5. How should the agent work: interview-first, guided drafting, assisted
   autonomy with human gates, or high autonomy with the same human-only gates?

Each question may use concise choice chips plus free text. An answer can trigger
one narrow clarification inside that category, such as the date of a disclosed
demo. If the opening message already answers a category, the agent records it
instead of repeating a robotic question.

After the first answered category, the agent creates an untitled matter and
opens the sidecar so every later answer has somewhere to land. Once all five
categories are covered, it moves into Source Lock. The early mechanism
interview supplies a real title and description. Creation is a result of the
conversation, not a separate form submission.

## Workflow state machine

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

State transitions depend on evidence and human decisions, not a number of
messages. A later disclosure, source, contributor, target, or mechanism can
invalidate an earlier gate. The system returns to that state, records the
reason, and repairs downstream summaries.

### State gates

| State | Conversation job | Gate to advance |
|---|---|---|
| Welcome | Explain the experience in one or two sentences. | Existing matter loaded or first quiz answer requested. |
| Triage Quiz | Route by idea state, disclosure state, objectives, available source material, and working style. | Matter created with all five orientation choices and any known disclosure/filing dates. |
| Source Lock | Separate earlier inventor source, later notes, external references, and generated material; capture contributors, ownership, and disclosure facts. | Sources classified and human-risk facts answered or visibly unresolved. |
| Objective Lock | Establish target, value thesis, commercial/public-benefit surface, privacy/trade-secret boundary, budget/timing, and 12/24-month success. | Inventor confirms or corrects the objective profile. |
| Core Mechanism | Elicit actors, components, relationships, operating cycle, causal mechanism, implementation, evidence, constraints, failures, and inventor-known alternatives. | Inventor can explain a coherent representative implementation. |
| Seed Expansion | Split the invention into distinct technical mechanisms and hidden control/evidence paths. | Multiple seeds confirmed by the inventor, or a recorded single-seed waiver. |
| Seed Assay | Apply preliminary closest-art, five-angle search, design-around pressure, evidence, and available IVS dimensions per seed. | Comparable, uncertainty-aware seed portfolio exists. |
| Terrain Selection | Compare standalone/combine/later/defer/no-file routes and purchased-with tradeoffs. | Inventor approves the terrain to stake. |
| Provisional Posture | Choose lean-core, disclosure reservoir, or layered provisionals and identify now/withheld/staged material. | Posture, dates, constraints, triggers, and inventor approval recorded. |
| Disclosure Build | Develop make/use support, alternatives, parameters, failures, examples, evidence, and fallback hooks for selected terrain. | Coherent candidate record with visible gaps and no silent source contamination. |
| Attack/Repair | Stress novelty assumptions, obvious combinations, abstract framing, support, priority, disclosures, terminology, and design-arounds. | Gaps prioritized and dispositioned; inventor confirms next move. |
| Ready/Handoff | Summarize coverage, uncertainty, sources, terrain, posture, dates, withheld/later material, and next decision. | Inventor chooses export, continued work, or a separately authorized next workflow. |

## Per-turn orchestration

Every substantive exchange follows this loop:

```text
ask one useful question
  -> receive answer
  -> classify provenance
  -> extract candidate record changes
  -> confirm when the change is consequential
  -> revision-check and update the matter
  -> reflect a compact “I captured…” summary when useful
  -> choose the highest-value unanswered question
```

The next question comes from the current gate and the largest material gap, not
from a static questionnaire. Low-risk organization can happen automatically
within the selected autonomy level. The inventor always controls source
classification, objective changes, conception/possession facts, seed and
terrain selection, disclosure posture, withheld matter, publication, filing,
spend, and final external actions.

If a record update is stale, the agent reloads and reconciles. If the sidecar
cannot open, the chat and record updates continue and the failure is reported
once without a retry loop.

## Record model within the current service

The matter stores the five orientation answers and the explicit workflow phase.
The nine working phases from Source Lock through Attack/Repair each have a
corresponding checkpoint for an approved summary and status. Welcome, Triage
Quiz, and Ready/Handoff are workflow phases without harvest cards.

The agent advances `workflow_phase`, maintains the current checkpoint, brief,
map, Reference Library, Decision Ledger, knowns, uncertainties, and next action.
Checkpoint status is derived from the conversation; the user is not expected to
administer it.

### Invention brief

The brief is generated from the conversation and kept in the inventor's
language. It covers problem, mechanism, intended result, alternatives, and open
questions. The user may edit it, but a blank brief is never presented as their
next task.

### Invention map

The map is a visual explanation and thinking canvas for components, actors,
inputs, outputs, steps, alternatives, evidence, assumptions, and questions. It
is not a formal patent drawing. The agent may append useful map elements as the
mechanism becomes clear; the user may rearrange or correct them in the sidecar.

### Reference Library

Every inventor material, patent publication, paper, product, standard, web
source, or research lead that shapes the matter can be recorded with:

- citation or stable link;
- source type and date;
- relevance and relationship to the matter;
- technical, seed, embodiment, product, market, and jurisdiction tags;
- provenance; and
- lead, reviewed, or verified status.

New research enters as a lead. “No result found” is a search-confidence gap,
not proof of novelty. Public sources that may need later patent-office
reference review are distinguishable from internal model analysis.

### Decision Ledger

The ledger records inventor-confirmed objective, source, seed, terrain,
embodiment, disclosure-posture, withheld-matter, and suggestion-disposition
decisions with rationale. A model recommendation does not become a human
decision merely because it appears in chat.

## Source and inventorship posture

Source Lock precedes model expansion. Preserve these categories:

- `priority-safe` — inventor material existing by the relevant date;
- `later-note` — inventor material added later;
- `external-reference` — public or third-party material;
- `generated` — model-created proposal or analysis;
- `IDS-candidate` — public reference potentially needing later formal review;
- `search-lead` — unverified research lead.

In a directed human-and-model session, begin with the directing human as the
inventor. Preserve their problem framing, constraints, steering,
understanding, selection, modification, integration, and adoption of the
settled solution. Do not run a detail-by-detail origin audit or discard a
supported concept merely because a model voiced an option first. Conversely,
model output alone is not earlier inventor source or proof of human possession.

## Portfolio gate

Before provisional drafting or formal figure work:

1. harvest multiple distinct technical seeds;
2. establish a terrain declaration for each seed or named seed family;
3. apply preliminary closest-art and design-around pressure;
4. assess available IVS dimensions with evidence level and coverage;
5. leave PAS and PSS unassessed until their required artifacts exist;
6. rank standalone, combine, later filing, defer, or no-file;
7. state what each combination or narrowing buys and gives up; and
8. obtain inventor selection.

A long draft created before this gate is a workflow failure, not progress.

## Score lenses

- **IVS — Invention Value Score:** seed-stage view of whether the selected
  terrain appears worth pursuing. It can begin during Seed Assay.
- **PAS — Priority Asset Score:** view of whether a complete provisional
  candidate or filed provisional actually captures the declared terrain. It
  remains unassessed before that artifact exists.
- **PSS — Prosecution Survival Score:** view of an actual later claim set. It is
  unavailable in the provisional product.

Always show coverage, evidence level, missing prerequisites, and reasoning.
Never merge the lenses into a single score or let a score silently shrink the
inventor's terrain.

## Provisional disclosure postures

The product presents the three postures only after terrain selection:

- **Lean-core priority stub:** the essential mechanism, relationships, workable
  implementation, and necessary alternatives/fallbacks receive the first date;
  nonessential know-how may remain withheld.
- **Disclosure reservoir:** the widest technically supported set of material
  alternatives and future paths is disclosed when optionality or imminent
  publication outweighs disclosure cost.
- **Layered provisionals:** a lean first layer is followed by planned later
  layers; every layer receives its own date and the earliest conversion
  deadline remains conspicuous.

The required decision record includes rationale, terrain needing the first
date, intentionally withheld or staged material, public-disclosure and foreign-
filing constraints, next trigger and target date, earliest known conversion
deadline, and inventor approval.

## Version-one boundaries

- One invention and one locally stored matter per intended Mind workflow.
- One configured agent may conduct the workflow; it is not represented as an
  independent council.
- Optional research uses only user-approved tools and connections.
- The product organizes and pressure-tests a working record. It does not
  determine patentability, guarantee priority, give a legal conclusion, or file
  an application.
- Formal drawings, non-provisional/international drafting, PSS, filing screens,
  signatures, certifications, payment, and submission are outside this product
  contract unless a later workflow is separately authorized.

## Acceptance criteria

A conforming first run has these observable properties:

1. The first screen of work is one conversational question, not a form or
   patent lesson.
2. The five triage categories are covered one at a time, already answered
   categories are not repeated, and the first answer creates the matter without
   a separate manual intake.
3. The Tomorrowkit tab opens beside chat after create or resume.
4. Every meaningful answer updates the matter before the next question.
5. Within the early interview, the brief and uncertainty record visibly grow.
6. The user is never asked to copy a prompt or manually mark checkpoint status.
7. Multiple seeds are harvested and confirmed before any drafting step.
8. Research leads retain provenance and are not silently marked verified.
9. Terrain selection and provisional posture require explicit inventor
   confirmation.
10. PAS stays unassessed until a provisional candidate or filed record exists;
    PSS is absent without an actual later claim set.
11. Forms remain optional review/correction surfaces rather than the primary
    path.
12. Resume continues from the next material gap instead of repeating onboarding.
