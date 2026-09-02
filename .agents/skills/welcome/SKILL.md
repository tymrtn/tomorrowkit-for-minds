---
name: welcome
description: Greet the user when a new project starts. This mind was created from the Tomorrowkit template, so the welcome introduces that template and immediately starts the invention conversation.
---

# Welcome the user (template: Tomorrowkit)

This mind was created from a template -- a published snapshot of apps
another mind built:

- Title: Tomorrowkit
- Slug: `tomorrowkit`
- Description: A private, conversational invention workspace: the Mind
  interviews a solo inventor and keeps a source-aware provisional-patent
  record beside the chat
- Manifest: `template.md` (at the repo root, with `template.toml` beside it)

Do ALL of the following in your FIRST response, in the same turn, without
waiting to be asked:

1. Open with a short CUSTOM welcome that names **Tomorrowkit** and gives the
   one-line description above. Do NOT use a generic "Welcome to Minds"
   greeting and do NOT offer a generic suggestions list.
2. Immediately read `template.md` at the repo root (reading the manifest in
   the first turn is required), then read
   `.agents/skills/tomorrowkit-provisional/SKILL.md` in full.
3. Tomorrowkit has no activation requirements: nothing to connect, no keys,
   nothing leaves the Mind. Say that in one sentence, then start the product.
   Run `uv run tomorrowkit-workspace list`. If a matter exists, read it with
   `uv run tomorrowkit-workspace show <matter_id>`, open the record beside the
   chat with `python3 system/scripts/layout.py open tomorrowkit`, give a
   one-sentence recap of where the work stopped, and ask the single next
   useful question for its workflow state. If no matter exists, welcome the
   inventor in one sentence and ask question one of the triage quiz:

   **"Where is this invention today: mostly in your head, captured in notes or
   a build, in a draft provisional, or already filed?"**

   If the user's opening message already answers one or more triage
   categories, record those answers instead of repeating the question. End
   your first response on that question. The `tomorrowkit-provisional` skill
   owns every later turn, record update, and human decision gate: after the
   first answered category it creates the matter and opens the tab. Do not
   send a patent-law lesson, a multi-field intake, a suggestions menu, or a
   prompt for the user to copy, and do not ask several questions in one
   message.

The manifest's "How to adapt it" section is the full script for anything
beyond the first run. Work through its adaptation bullets only after a matter
exists and only if the user asks.

This repo holds exactly one template. If `template.toml` lists `[[lineage]]`
entries, those are the templates this one was built on -- each with the repo
URL and commit it was taken at, so you can go read any of them at the exact
state that was used. They are provenance, not something to adapt here.
