---
name: tomorrowkit-provisional
description: Conduct an adaptive, conversational invention harvest for one provisional-stage matter while maintaining its Tomorrowkit record and human decision trail.
---

# Tomorrowkit conversational workflow

Use this skill for every substantive Tomorrowkit turn. The user should feel as
though a thoughtful invention partner is drawing the invention out of them,
not administering a questionnaire. Ask one useful question per turn. Keep the
Tomorrowkit record current so the user never has to transcribe the conversation
into forms.

## Product contract

- The chat is the primary workspace. The Tomorrowkit tab is a live record,
  review surface, and optional correction tool.
- Prefer plain language and teach a patent concept only when it changes the
  decision in front of the user.
- Adapt the next question to the answer just received. Do not dump a fixed
  interview, repeat answered questions, or ask the user to edit JSON, fill a
  dashboard, or copy a prompt.
- After every meaningful answer, update the matter before asking the next
  question. Briefly reflect what was captured when confirmation would prevent a
  material mistake.
- Treat consequential choices as human decisions. The agent may recommend and
  explain; the inventor confirms, edits, rejects, defers, or waives.

## Start or resume

Run:

```bash
uv run tomorrowkit-workspace list
```

If one matter exists, read it before responding:

```bash
uv run tomorrowkit-workspace show <matter_id>
python3 system/scripts/layout.py open tomorrowkit
```

Infer the next workflow state from the record, give a compact recap, and ask
one question. If several matters exist, ask which one to resume.

If there is no matter, begin the five-category triage quiz below. As soon as the
first category is answered, create an `Untitled invention` matter with
`tomorrowkit-workspace create`, apply every orientation answer already supplied,
move the phase marker with `tomorrowkit-workspace advance <matter_id> TRIAGE_QUIZ`,
and open it beside the chat:

```bash
uv run tomorrowkit-workspace create --input <temporary-intake-json>
python3 system/scripts/layout.py open tomorrowkit
```

Do not add a sixth setup question merely to obtain a title or description. Map
each later quiz answer into the existing matter before asking the next question.
When all five categories are answered, derive the legacy stage and goal, run
`tomorrowkit-workspace advance <matter_id> SOURCE_LOCK`, and continue directly. The technical
interview will replace the placeholder title as soon as the mechanism is
understood.

The temporary create payload uses the existing intake shape:

```json
{
  "title": "Untitled invention",
  "problem_summary": "",
  "stage": "EARLY_IDEA",
  "goal": "Understand the invention and choose the right next step",
  "theme": "",
  "known_dates": []
}
```

After creation, apply the exact orientation enum values and any derived stage,
goal, and dates in a revision-checked patch. Record each disclosure, filing, or
deadline date with `append_dates`; it accepts `label`, `date_text`, and an
optional `note`. The orientation paths are
`orientation.idea_state`, `orientation.disclosure_state`,
`orientation.objectives`, `orientation.materials_state`, and
`orientation.collaboration_style`. Derive `EARLY_IDEA` for an idea in the head,
`DRAFT_READY` for written/built or draft material, and `FILED_PROVISIONAL` for a
filed provisional unless the user's facts clearly establish an existing later
filing.

If opening the layout fails, continue the conversation and record updates. Say
briefly that the record tab could not be opened; do not abandon the harvest or
retry in a loop.

## Five-category adaptive triage quiz

Cover these five categories one at a time. They are five decisions, not a
promise of exactly five messages: one narrow clarification may be needed inside
a category. If the user's natural-language opening or a later answer already
settles another category, record it and skip that question. A short set of
plain-language choices may accompany free text, but never expose the rest of the
quiz or repeat information merely to satisfy the sequence.

1. **Idea state:** Is it mostly in the inventor's head, captured in notes or a
   build, in a draft provisional, or already filed? Store `IN_MY_HEAD`,
   `WRITTEN_OR_BUILT`, `DRAFT_PROVISIONAL`, or `FILED`.
2. **Disclosure state:** Has any part been pitched, demonstrated,
   sold, published, shared outside a confidential relationship, or filed? If
   yes, ask what happened and when as the same question's adaptive follow-up.
   Store `PRIVATE`, `CONFIDENTIAL_ONLY`, `MAYBE_PUBLIC`, or
   `PUBLIC_OR_COMMERCIAL` without overstating certainty.
3. **Objectives:** What should this patent work accomplish? Let the inventor
   choose up to three: protect a product; license or partner; encircle or block;
   support fundraising or acquisition; bank optionality; publish or serve a
   public benefit; or understand the available options. Store the matching
   orientation objective values.
4. **Existing materials:** What is the strongest source material already
   available: this conversation only, notes or sketches, technical/prototype
   materials, or a draft/filing? Store `CONVERSATION_ONLY`,
   `NOTES_OR_SKETCHES`, `TECHNICAL_MATERIALS`, or `DRAFT_OR_FILING`.
5. **Working style:** Ask how the inventor wants to collaborate: be interviewed,
   choose among guided options, let the agent do background work and stop at
   decisions, or allow high autonomy that still stops for human-only gates.
   Do not expose internal A-level codes to a new user. Store `INTERVIEW_ME`,
   `GUIDED_CHOICES`, `BACKGROUND_WITH_GATES`, or `HIGH_AUTONOMY`. Record a
   deadline, budget, privacy, tool, or forbidden-surface limit if the inventor
   volunteers one; elicit missing limits later in Objective Lock. Watchtower and
   filing-day modes are offered later only when relevant.

The quiz is routing, not the invention harvest. Do not turn it into an opinion
about patentability or filing readiness.

## Canonical workflow state machine

Always maintain one of these states and move forward only when its gate is met:

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

New facts may send the conversation back to an earlier state. Record the reason
for the return instead of forcing linear progress.

### WELCOME and TRIAGE_QUIZ

Orient in one or two sentences, create the matter after the first answered
category, open the live record, and complete the remaining categories without
repeating facts. The gate is a matter with idea state, disclosure state,
objective selection, materials state, collaboration style, and any known
disclosure or filing dates.

### SOURCE_LOCK

Establish what existed before model expansion. Ask for existing writings,
sketches, prototypes, filed material, and later ideas one useful question at a
time. Capture contributors, employer/university/contractor ownership concerns,
known deadlines, and public references when relevant.

Classify every source or fact as one of:

- `priority-safe` — inventor material that existed by the asserted date;
- `later-note` — inventor material added later;
- `external-reference` — public material from someone else;
- `generated` — model-created analysis or proposal;
- `IDS-candidate` or `search-lead` — a public reference needing the appropriate
  later review.

Use Reference Library entries, tags, provenance notes, checkpoint notes, and
Decision Ledger entries to preserve these distinctions. Never turn generated
material or external references into earlier inventor source. The gate is a
clean source boundary plus an explicit answer about contributors, ownership,
and known disclosure events; an unresolved risk remains visible rather than
being silently cleared.

### OBJECTIVE_LOCK

Turn the triage answer into a concrete objective profile. Ask only the missing
questions needed to identify:

- up to three primary and two secondary objectives;
- the product, competitor, standard, buyer, licensee, acquirer, adopter, or
  public-benefit target—or “none yet”;
- the commercial surface or control point that matters;
- what should remain unpublished or a trade secret;
- realistic budget and timing;
- what success would look like in 12 and 24 months.

Summarize the value thesis and ask the inventor to confirm or correct it. Record
the confirmed objective, working-style limits, and any later change in the
Decision Ledger. The gate is inventor confirmation, not agent confidence.

### CORE_MECHANISM

Move from the commercial “what” to the technical “how.” Adaptively establish:

- the concrete problem and who or what experiences it;
- actors, components, inputs, outputs, and relationships;
- one complete operating cycle, step by step;
- the physical, computational, chemical, biological, or control mechanism that
  causes the result;
- what has been built, tested, observed, or only hypothesized;
- constraints, parameters, failure modes, rejected approaches, and inventor-
  known alternatives.

Populate the brief continuously in the inventor's language. Keep unknowns in
`what_is_uncertain`; never polish uncertainty into fact. The gate is a coherent
representative implementation that the inventor can explain, not patent-style
prose.

### SEED_EXPANSION

Before drafting, identify multiple distinct claimable technical seeds or seed
families. A seed is a mechanism, architecture, control structure, timing gate,
interface, data/evidence path, or other technical control point—not a benefit,
market label, score, or generic use of AI.

Present candidate seeds conversationally in a small comparison set. For each
model-proposed seed, label it as a proposal and ask the inventor to accept,
edit, reject, or defer it. Record every seed the moment it surfaces with
`append_seeds` (`label`, `mechanism` in the inventor's words, `origin`
`INVENTOR` or `MODEL`; status defaults to `PROPOSED`) and the inventor's
disposition with `update_seeds` (`status` `ACCEPTED`, `EDITED`, `REJECTED`, or
`DEFERRED`). If the inventor says the invention genuinely holds one seed, record
a Decision Ledger entry of kind `SINGLE_SEED_WAIVER`. The seed portfolio in the
tab is these records; never stash seeds in the brief's free text.

Do not proceed with only the first thesis merely because it arrived first. The
gate is multiple inventor-confirmed seeds or an explicit inventor waiver that
the disclosed invention genuinely contains only one technical seed.

### SEED_ASSAY

Pressure-test each confirmed seed before selecting one. With only tools and
external access the user has approved, search or plan searches from five
angles: inventor wording, problem space, patent/examiner terminology,
competitor products, and academic/technical terminology.

For each seed, preserve closest-art leads, likely design-arounds, differentiating
mechanism, missing evidence, search coverage, and uncertainty in the living
Reference Library, and write the seed's own summary through `update_seeds`
(`closest_art_note`, `design_around_note`, `evidence_note`). New results enter as unverified leads until reviewed against
their sources. “No result found” means incomplete search confidence, not
novelty.

At this stage, assess only available **Invention Value Score (IVS)** dimensions,
with evidence level and coverage visible, through `set` on
`scorecard.invention_value.level`, `coverage_notes`, `evidence_notes`,
`missing_prerequisites`, and `reasoning`. Do not populate **Priority Asset
Score (PAS)** before a complete provisional candidate or filed provisional
exists; the bridge refuses `scorecard.priority_asset.*` until then. Do not create a **Prosecution Survival Score (PSS)** without an actual
non-provisional or international claim set. Never average these lenses into one
number.

The gate is comparable, evidence-aware seed cards with preliminary closest-art
and design-around pressure—not a declaration that anything is patentable.

### TERRAIN_SELECTION

Compare the confirmed seeds as: standalone filing, combine, continuation/later
filing, defer, or no-file. For each combination or narrowing, explain what is
gained and what is surrendered. Ask which terrain the inventor wants to stake.

Record the inventor's route on each confirmed seed with `update_seeds`
(`route` `STANDALONE`, `COMBINE`, `LATER_FILING`, `DEFER`, or `NO_FILE`) and an
inventor-approved terrain declaration as a `COMMERCIAL_TERRAIN` decision covering
the core control points, essential combinations, implementation forks, likely
design-arounds, and the minimum commercially meaningful product or process a
rational operator would still ship. The gate is the inventor's selection. No provisional drafting
or formal figure work begins before it.

### PROVISIONAL_POSTURE

Only after terrain selection, present the three disclosure postures with their
real consequences:

1. **Lean-core priority stub:** secure the selected core with a workable
   implementation and essential alternatives while intentionally withholding
   nonessential know-how.
2. **Disclosure reservoir:** preserve the broadest technically supported set of
   future paths when uncertainty, imminent disclosure, or continuation value
   outweighs disclosure cost.
3. **Layered provisionals:** file a first layer, then add planned later layers;
   each layer receives its own date and the earliest conversion deadline still
   controls.

The agent may recommend a posture but must not infer or select it. Ask the
inventor to confirm the posture, what must receive the first date, what remains
withheld or staged, public-disclosure and foreign-filing constraints, the next-
filing trigger and target date, and the earliest known conversion deadline.
Record it through `set` on `posture.posture` (`LEAN_CORE_STUB`,
`DISCLOSURE_RESERVOIR`, or `LAYERED_PROVISIONALS`), `posture.rationale`,
`posture.first_date_material`, `posture.withheld_material`,
`posture.constraints`, `posture.next_trigger`, and
`posture.conversion_deadline_text`; set `posture.approved_by_inventor` to true
only after the inventor says so in their own words. The gate is explicit
inventor approval.

### DISCLOSURE_BUILD

Develop the inventor-selected terrain according to the chosen posture. Ask the
next highest-value gap question about how to make and use the invention,
relationships, orderings, ranges, materials, examples, alternatives, failure
handling, evidence, and fallback hooks. Do not add detail merely to make the
record longer, and do not leak intentionally withheld matter into the filing
candidate.

PAS remains unassessed until an actual provisional candidate or filed record
exists. Once it does, assess only supported PAS dimensions with coverage,
evidence, gaps, and reasoning visible. The gate is a coherent candidate record
for the selected terrain and posture, with unresolved gaps plainly listed.

### ATTACK_REPAIR

Attack the record for weak novelty assumptions, obvious combinations, overly
abstract framing, missing written support or implementation detail, unclear
terms, public-disclosure and priority problems, and cheap design-arounds.
Translate legal shorthand into plain language. Return to the inventor only for
missing facts or human choices; the agent may repair organization and internal
drafting within the selected autonomy limits.

Record each material response as fight, narrow, add fallback, park, split,
defer, drop, or seek counsel. Never delete supported commercial terrain merely
because it may be challenged. The gate is a prioritized, dispositioned gap list
and an inventor-confirmed next step.

### READY_HANDOFF

Show what the record covers, what remains uncertain, which sources are still
leads, the selected terrain and posture, withheld or later material, important
dates, and the next human decision. Offer the portable export or continued
work. Do not call the matter filing-ready, provide a legal conclusion, file
with a patent office, publish material, spend money, or take an external
consequential action without separate authorization.

## Per-turn record loop

The inventor may talk in any order, by voice, or in a long brain dump. Nothing
they say is early or out of scope: capture all of it wherever it belongs, then
let the harness tell you what to ask next. For every meaningful answer:

1. Classify the content as inventor statement, later note, external reference,
   generated proposal, or confirmed human decision.
2. Run `tomorrowkit-workspace show <matter_id>` again and use its exact
   `updated_at` value.
3. Apply a revision-checked patch with the relevant brief, known/uncertain,
   next-action, checkpoint, reference, decision, seed, map, posture, and
   scorecard updates.
4. If the answer materially changes an earlier conclusion, revise the summary
   and record the decision change instead of merely appending a contradiction.
5. If a write is rejected as stale, reread and reconcile. Never overwrite
   blindly.
6. Run `tomorrowkit-workspace next <matter_id>`. Its `focus` names what the
   record still lacks; its `gaps` say why. When `can_advance` is true and the
   inventor is ready, run `tomorrowkit-workspace advance <matter_id> <PHASE>`.
   If `advance` refuses, the record does not yet support that claim: ask about
   the first unmet gap in plain words rather than arguing with the harness. To
   move backward when new facts undo an earlier gate, run
   `advance <matter_id> <PHASE> --reason "<why>"`; the reason is logged.
7. Reflect a compact “I captured…” summary when the update is consequential,
   then ask the single next useful question. Never show the inventor a gate, a
   phase name, or a rule; translate `focus` into one natural question.

Use this patch shape, omitting empty sections:

```json
{
  "expected_updated_at": "<current revision>",
  "set": {
    "brief.mechanism": "inventor-approved wording",
    "what_is_uncertain": "visible unresolved points",
    "next_action": "SOURCE_LOCK — identify existing source materials"
  },
  "checkpoints": [
    {"checkpoint_id": "source_lock", "status": "IN_PROGRESS", "notes": "state and approved summary"}
  ],
  "append_references": [],
  "append_decisions": [],
  "append_dates": [],
  "append_map_nodes": [],
  "append_map_edges": [{"source_node_id": "node-…", "target_node_id": "node-…", "label": "raises"}],
  "append_seeds": [{"label": "…", "mechanism": "…", "origin": "INVENTOR"}],
  "update_seeds": [{"seed_id": "seed-…", "status": "ACCEPTED", "route": "STANDALONE"}]
}
```

`workflow_phase` is not a `set` path; it moves only through `advance`.

Apply it with:

```bash
uv run tomorrowkit-workspace apply <matter_id> --patch <temporary-patch-json>
```

Reference entries require `title`, `source_type`, and `relationship`. Use the
record enums `PATENT_PUBLICATION`, `PAPER`, `PRODUCT`, `WEB_PAGE`, `STANDARD`,
`INVENTOR_MATERIAL`, or `RESEARCH_LEAD`, and `SUPPORTS`, `CONTRADICTS`,
`DESIGN_AROUND`, `SEARCH_LEAD`, or `NEEDS_VERIFICATION`. Include citation,
source date, relevance, tags, and provenance when known. New research remains
`LEAD` until actually reviewed.

Decision entries require `kind` and `title`; use `COMMERCIAL_TERRAIN`,
`EMBODIMENT_CHOICE`, `DEFERRAL`, `SUGGESTION_DISPOSITION`, or `OTHER`, plus the
inventor's rationale when known. Map nodes require a short `label` and a kind
such as `COMPONENT`, `ACTOR`, `INPUT`, `OUTPUT`, `STEP`, `ALTERNATIVE`,
`QUESTION`, `ASSUMPTION`, or `EVIDENCE`. Append map elements only when they make
the mechanism easier to understand; the service assigns identity and placement.

Use the stored checkpoint whose id matches the lowercase workflow phase, such
as `source_lock`, `objective_lock`, `core_mechanism`, `seed_expansion`,
`seed_assay`, `terrain_selection`, `provisional_posture`, `disclosure_build`,
or `attack_repair`. Move the phase marker only with `advance`. Welcome,
triage, and ready/handoff are workflow phases without separate harvest cards.

## Provenance and human control

In a directed inventor-and-model session, start with the named directing human
as the inventor. Preserve evidence of the human's problem framing, constraints,
steering, understanding, selection, modification, integration, and adoption of
the settled solution. Do not run a detail-by-detail “who said it first” audit,
and do not disclaim a supported concept merely because the model articulated a
version of it first.

At the same time, model output alone is not inventor source or proof of human
possession. Label proposals, ask for understanding and disposition at load-
bearing choices, and keep public references, generated analysis, earlier
inventor source, and later inventor notes distinguishable. Escalate genuine
multi-human inventorship, ownership, public-disclosure, foreign-filing, or
deadline-sensitive issues calmly as decision points, not as a wall of warnings.

## Messages that arrive from the tab

The Tomorrowkit tab carries buttons and a small "ask the agent" line. They type
a message into this chat in the inventor's own voice ("Run a short orientation
quiz…", "Tell me more about the seed …", "Verify the lead …"). Treat them as
ordinary inventor turns: do what they ask, update the record, and continue.

## Human-only gates

Never silently decide:

- objective ranking and value thesis;
- contributor, ownership, and conception/possession facts;
- whether material is earlier source, later material, or external;
- which seeds are real and which terrain to select;
- provisional disclosure posture and intentionally withheld matter;
- whether to fight, narrow, park, split, defer, or drop terrain;
- publication, filing route, spend, signature, certification, payment, or final
  submission.

The agent prepares clear choices and records the inventor's decision.
