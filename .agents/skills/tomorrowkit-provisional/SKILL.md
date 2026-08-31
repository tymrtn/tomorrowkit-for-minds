---
name: tomorrowkit-provisional
description: Guide one inventor through a private, provisional-stage invention harvest while maintaining the Tomorrowkit visual matter record.
---

# Tomorrowkit provisional workflow

Use this skill for every substantive Tomorrowkit conversation. The user talks
to you in the Mind; you maintain the visual record with the deterministic
`tomorrowkit-workspace` command. Never ask the user to copy prompts or edit
workspace files.

## Start or resume

Run `uv run tomorrowkit-workspace list`. If there is one matter, run
`uv run tomorrowkit-workspace show <matter_id>` before continuing. If none
exists, gather a working title, the core problem/approach, stage, important
dates, and immediate goal one question at a time. Write a temporary intake JSON
object and run:

```bash
uv run tomorrowkit-workspace create --input /tmp/tomorrowkit-intake.json
```

One Mind is one invention. If more than one matter exists, ask which to resume
rather than guessing.

## Maintain the record

Before every write, run `show` again and use its exact `updated_at` value in a
temporary patch file:

```json
{
  "expected_updated_at": "<current revision>",
  "set": {
    "brief.problem": "inventor-approved wording",
    "what_is_uncertain": "clearly labeled uncertainty",
    "next_action": "one plain-language next step"
  },
  "checkpoints": [
    {"checkpoint_id": "intake", "status": "IN_PROGRESS", "notes": "summary"}
  ],
  "append_references": [],
  "append_decisions": []
}
```

Apply it with:

```bash
uv run tomorrowkit-workspace apply <matter_id> --patch /tmp/tomorrowkit-patch.json
```

The command validates the schema and rejects stale revisions. If it rejects a
write, read the matter again and reconcile; never overwrite blindly.

Reference entries require `title`, `source_type`, and `relationship`.
Appropriate enum values include `PATENT_PUBLICATION`, `PAPER`, `PRODUCT`,
`WEB_PAGE`, `STANDARD`, `INVENTOR_MATERIAL`, or `RESEARCH_LEAD`, and
`SUPPORTS`, `CONTRADICTS`, `DESIGN_AROUND`, `SEARCH_LEAD`, or
`NEEDS_VERIFICATION`. New sources default to `LEAD`. Include a stable citation,
source date, relevance note, tags, and provenance whenever available.

Decision entries require `kind` and `title`; kinds include
`COMMERCIAL_TERRAIN`, `EMBODIMENT_CHOICE`, `DEFERRAL`,
`SUGGESTION_DISPOSITION`, and `OTHER`. Record only decisions the user actually
made or confirmed.

## Four checkpoints

Move conversationally and revisit earlier checkpoints when new information
changes the record.

1. **Intake interview** — understand the problem, mechanism, intended result,
   alternatives, what exists or has been tested, contributors, and known
   disclosures or filings. Preserve the inventor's language. Ask one question
   at a time.
2. **Prior-art prospecting** — generate search terrain, then use only tools the
   user has enabled. Add patents, papers, products, standards, and search leads
   to the Reference Library with provenance. Do not characterize a lead as
   verified merely because a model found it.
3. **Disclosure development** — pressure-test whether a technically skilled
   reader could understand how to make and use the described embodiments.
   Ask about omitted steps, mechanisms, ranges, failure cases, and alternatives.
   Clearly distinguish user statements from model-proposed possibilities.
4. **Adversarial review** — identify missing support, weak novelty assumptions,
   unexplained terminology, omitted variants, contradictory references, and
   unresolved inventorship questions. Produce prioritized gaps, not a verdict.

## Inventorship and provenance

- Human inventorship cannot be supplied by an AI system. Keep the user's
  contributions, source materials, model suggestions, and later approvals
  distinguishable.
- Never silently convert a model suggestion into an inventor fact or decision.
- Do not state that an idea is patentable, that a provisional guarantees
  priority, or that the record is filing-ready.
- Do not disclose invention material outside tools and providers the user has
  chosen for this Mind.
- For an unusually valuable, disputed, employer-owned, or deadline-sensitive
  matter, calmly flag that tailored legal advice may be worthwhile.

## Escalation and improvement

When the workflow encounters a case it cannot represent, do not improvise a
silent schema change. Complete the immediate conversational task if safe, then
propose a concrete skill, schema, validator, or regression-fixture change for
the user to approve. Runtime novelty should improve the reusable workflow only
after validation.
