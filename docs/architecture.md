# Tomorrowkit for Minds — First Inspiration Architecture

## Purpose

Create a local-first, single-inventor provisional-patent workspace inside Minds. It should give a person a calm orientation, turn one rough idea into one private matter workspace, and help them work productively with their existing local AI agent.

This is deliberately not a full patent-filing product, a formal drawing tool, or a multi-model council. It is the useful, trustworthy first layer of Tomorrowkit.

## Product promise

**One invention, one workspace.**

The product helps an inventor go from “I have an idea” to an organized, evidence-aware provisional-workspace record. The inventor retains control of their materials and uses an AI account they are comfortable using for sensitive work.

The paid or advanced future of the product is not a tollbooth around the inventor’s work. It adds convenience and higher-assurance capabilities—especially a genuine independent model council—while the user keeps a portable matter record.

## Version-one boundary

### Include

- A friendly orientation to the patent journey, key vocabulary, and Tomorrowkit stages.
- A short intake that creates one dedicated matter workspace for one invention.
- A structured provisional-stage workspace.
- A guided harvesting workflow run through the user’s existing local agent.
- A lightweight visual Invention Map for systems, flows, alternatives, and open questions.
- A living Reference Library for prior art, sources, and research leads.
- A plain-language stage view, decision ledger, and portable export.
- Practical privacy guidance: use an account appropriate for sensitive work, disable training where the provider makes that available, and connect only sources that help.

### Exclude

- A multi-provider council, automatic parallel model routing, or a claim that independent council review already exists.
- Formal patent drawing generation, formal drawing-sheet formatting, or non-provisional/PCT figure export.
- Filing automation, fee payment, USPTO submission, or legal conclusions.
- Silent public sharing, outbound messages, or consequential external actions.
- Non-provisional/PCT prosecution scoring and workflows.

## Experience flow

```text
Orientation → minimal confidential idea brief → create matter workspace
→ guided invention harvest → organize sources and decisions
→ develop provisional disclosure readiness → export or continue
```

### Orientation

The orientation is a useful product in its own right. It should explain, in plain English:

1. What a patent process is trying to protect.
2. The difference between an idea, an invention disclosure, a provisional application, and a later examined application.
3. Essential vocabulary: priority date, disclosure, claims, provisional application, non-provisional application, PCT, and new matter.
4. The Tomorrowkit stage map.
5. The inventor’s human role when using AI: understand, select, modify, and approve important decisions.
6. The three high-level moments that matter: before public disclosure, before filing a provisional, and before the later conversion decision.

The orientation should be calm and practical rather than fear-driven. It is not legal advice, and it should not overwhelm a new inventor with a terms-of-service or compliance lecture.

### Minimal handoff

When a user chooses **Create my invention workspace**, collect only what is needed to create a useful starting point:

- Working title.
- A short description of the problem and intended approach.
- Current stage: early idea, draft-ready, filed provisional, or existing application.
- Known important dates or prior public disclosures, if the user knows them.
- The user’s immediate goal.
- An optional visual theme or industry cue.

Do not hard-code a long invention interview into the UI. The detailed, adaptive harvest belongs to the Tomorrowkit guidance supplied to the user’s agent.

## Matter workspace

Each matter should start with these connected areas:

### Matter Home

- Current plain-language stage.
- What is known.
- What remains uncertain.
- Next recommended action.
- Important dates that the user has entered.

### Invention Brief

An evolving, human-reviewable account of the problem, proposed mechanism, intended result, alternatives, and unanswered questions. Preserve the inventor’s language rather than replacing it with polished patent prose prematurely.

### Harvesting Room

The place where the user works with their existing agent. Tomorrowkit’s existing intake, prospecting, drafting, and adversarial guidance remains the workflow intelligence. The UI provides checkpoints and artifacts; it does not freeze the process into a fixed questionnaire.

### Invention Map

A simple, editable visual workflow canvas—not a patent figure editor.

It should let the inventor and agent lay out:

- Components, actors, inputs, outputs, and steps.
- Relationships and flows.
- Alternative embodiments and implementation branches.
- Questions, assumptions, evidence links, and unresolved areas.

It is for thinking, explaining, and improving disclosure. It must not claim to produce formal patent drawings or offer filing-standard export.

### Reference Library

This is a central version-one artifact, not an optional add-on. It turns scattered research into an organized, inspectable record and demonstrates the value of structured Tomorrowkit work over ad hoc chat.

Each entry should support:

- Citation or stable source link.
- Source type: patent publication, paper, product, web page, standard, inventor material, or research lead.
- Short plain-language relevance note.
- Tags for technical concept, claim family, embodiment, competitor/product, market, jurisdiction, and status.
- Relationship to the matter: supports, contradicts, raises a design-around, creates a search lead, or needs verification.
- Date and provenance metadata when available.
- A verification state: lead, reviewed, or verified.

The Reference Library is an evolving research and disclosure artifact. It should not call itself a filed information-disclosure statement or imply that it satisfies any formal filing obligation. Its purpose is to make later review, counsel handoff, and any formal reference process dramatically easier.

### Decision Ledger

Capture important human decisions and their rationale, including:

- What terrain matters commercially.
- Which embodiment or route the inventor selected.
- What was deferred, withheld, or requires more evidence.
- Which sources and model suggestions were accepted, changed, or rejected.

### Scorecard

For the provisional product, render only the two relevant Tomorrowkit lenses:

- **IVS — Invention Value Score:** whether the inventor-approved terrain appears worth pursuing.
- **PAS — Priority Asset Score:** whether the provisional record captures that terrain.

Never merge these lenses into a single score. Show coverage, evidence level, missing prerequisites, and the underlying reasoning. The later **PSS — Prosecution Survival Score** belongs only in the non-provisional/PCT product.

Version one may use one agent and structured self-review. It must not represent that as independent council scoring.

### Export and handoff

Give the user a portable package containing their brief, map, reference library, decision ledger, and selected workspace artifacts. The export is theirs to keep, adapt, and share selectively with counsel or collaborators.

## Future capability: Council Room

The Council Room is a defined future extension, not a disguised version-one feature.

It should eventually provide separate adviser roles with independent contexts:

- Lead architect/drafter.
- Adversarial patent reviewer.
- Landscape and commercialization strategist.
- Reconciler/operator.

The interface must support private conversations with each role, sending a revision to the whole council, preserving disagreement, and recording the human disposition. It must not average away conflicting views or allow a drafter to be the sole grader of its own work.

This requires a genuine Minds extension or fork for multi-provider routing, context separation, permissions, and structured reconciliation.

## Design principles

1. **Human agency first.** The inventor owns the matter, makes consequential decisions, and can export their work.
2. **Local-first by default.** External connections are useful optional inputs, not a requirement to start.
3. **Structured, not bureaucratic.** Every artifact should make the next decision easier.
4. **Visible uncertainty.** Unknowns stay visible; missing evidence is not silently converted into confidence.
5. **No false formality.** Do not present provisional aids as formal drawings, scores as legal conclusions, or workflow guidance as filing execution.
6. **Progressive disclosure.** Teach the next relevant concept when it becomes useful instead of front-loading a course in patent law.
7. **A complete free baseline.** Advanced service may sell convenience, coordination, and assurance, never ownership of the user’s invention record.

## Build request for Minds

Build a polished, private, local-first Minds inspiration called **Tomorrowkit Orientation & Provisional Workspace**.

Start with the orientation and matter-creation flow, then create the workspace areas described above. Favor a warm, legible, visual interface over a generic dashboard. Treat the Reference Library and Invention Map as the primary immediately visible artifacts after Matter Home.

Use the user’s existing local agent for guided harvesting. Do not claim a multi-model council, formal patent drawing capability, filing automation, legal advice, or external action-taking. Keep all matter contents editable and exportable.

When an exact Minds platform capability is uncertain, build the clearest safe in-workspace version and explicitly mark the limitation rather than inventing an integration.
