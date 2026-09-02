---
title: "Tomorrowkit"
description: "A private, conversational invention workspace: the Mind interviews a solo inventor and keeps a source-aware provisional-patent record beside the chat"
thumbnail: "template.svg"
version: v4
format: v2
---

# Tomorrowkit

This file is the manifest for the **Tomorrowkit** template (slug:
`tomorrowkit`). It is the one document a future agent reads to understand,
present, and adapt this template. If you are an agent in a mind that was
created from this template, this file is your script: read all of it, then
follow "How to adapt it" below.

## What it is

A private, conversational invention workspace: the Mind interviews a solo
inventor and keeps a source-aware provisional-patent record beside the chat.

Tomorrowkit solves the problem that AI made patent *drafting* cheap without
solving what is actually worth protecting, what should stay out of a first
disclosure, and how to prove what the human inventor conceived. The inventor
talks through one invention in chat. The agent asks one useful question at a
time and, after every meaningful answer, updates a structured matter record:
an invention brief in the inventor's own words, a visual Invention Map, a
Reference Library with provenance labels, a Decision Ledger of the human
choices and their reasons, two provisional-stage score lenses that are never
averaged, and a Markdown/JSON/ZIP export. The Tomorrowkit tab opens beside the
conversation and shows that record taking shape; it is a review and
correction surface, never a form the inventor has to fill in. What the user
sees when it is running: a chat asking the next question about their
mechanism, and a tab titled "Continue with Tomorrowkit" that shows what has
been captured, what is still open, and where the conversation is focused.

## How it works

The snapshot includes these paths (each is a repo-root-relative path copied
from the original mind onto a clean default-workspace-template base):

- `system/apps/tomorrowkit`
- `.agents/skills/tomorrowkit-provisional`

`system/apps/tomorrowkit` is the record service and the agent's bridge to it,
one Python workspace package:

- `src/tomorrowkit/runner.py` is the Flask app: the matter list and
  orientation page at `/`, the record page at `/matter/<id>`, the JSON API
  under `/api/matters`, and the ZIP export. Its `tomorrowkit` console script
  (`tomorrowkit.runner:main`) serves on `127.0.0.1`, port `8090` (overridable
  via `TOMORROWKIT_PORT`).
- `src/tomorrowkit/agent_tools.py` is the `tomorrowkit-workspace` console
  script: `list`, `show`, `create`, `orient`, `apply`, `next`, and `advance`.
  The agent uses it to read and update the record without HTTP. `apply` takes
  a revision-checked patch (`expected_updated_at` copied from `show`) and only
  sets allow-listed fields (brief, posture, scorecard) or appends references,
  decisions, dates, checkpoints, map nodes and edges, and seeds. `next` reports
  what the record still lacks before its phase marker can move and what to ask
  about; `advance` moves the marker when the record supports it and logs a
  reason when moving back. `src/tomorrowkit/steering.py` holds those gate rules.
- `src/tomorrowkit/data_types.py` holds the Pydantic record model
  (`MatterDocument` and its parts, including the seed portfolio, the posture
  plan, and the owning chat agent); `storage.py` writes one JSON file per
  matter under `DATA_DIR/matters/` with an advisory file lock, an atomic
  replace, and a compare-and-swap on `updated_at` so the chat and the tab can
  edit the same matter safely; `export.py` renders the portable ZIP.
- `src/tomorrowkit/assets/` is the frontend: two Jinja templates, plain CSS
  and JS, and the bundled fonts (Source Serif 4, Archivo, IBM Plex Mono under
  the OFL, see `THIRD_PARTY_NOTICES.md`). Every URL is relative, so the app
  works at its own origin and when addressed directly on its port.

`.agents/skills/tomorrowkit-provisional/SKILL.md` is the interview. It carries
the gated state machine (Welcome, Triage Quiz, Source Lock, Objective Lock,
Core Mechanism, Seed Expansion, Seed Assay, Terrain Selection, Provisional
Posture, Disclosure Build, Attack/Repair, Ready/Handoff), the per-turn loop
(`show`, patch, `apply`, reconcile if stale), the provenance rules, and the
decisions only the inventor may make.

At runtime one supervisord program named `tomorrowkit` (added to
`system/supervisord.conf` for this snapshot) runs the service. Its command
first calls `python3 system/scripts/forward_port.py --url http://localhost:8090
--name tomorrowkit --icon-file system/apps/tomorrowkit/icon.svg --program
tomorrowkit`, which registers the app so it renders as its own tab at its own
origin, and then runs `uv run tomorrowkit`. The workspace wiring in
`pyproject.toml` (the `tomorrowkit` entry in `[project].dependencies`, the
`system/apps/*` workspace member glob, and the `tomorrowkit = { workspace =
true }` source) is what makes `uv run tomorrowkit` and `uv run
tomorrowkit-workspace` resolve. The agent opens the tab beside the chat with
`python3 system/scripts/layout.py open tomorrowkit`. On-disk state lives under
`data/.apps/tomorrowkit/` (overridable via `TOMORROWKIT_DATA_DIR`).

## Recipe

This template is version `v4`. It is not a fork of the
workspace it came from -- it is DERIVED from it by a recipe: include these
paths, leave these out, apply these published-version rules. An update re-runs
the recipe against the current workspace and publishes the result as the next
version, so anything excluded stays excluded even though it still exists in the
source workspace.

The recipe is machine-read, so it lives in the sibling
[`template.toml`](template.toml) -- its `[recipe]` table -- along with
the structured requirements and the environment this template needs
installed. That file is authoritative for all of it; this one holds the prose.

## Requirements

Everything the adopting mind must deal with before this template is really
theirs. Two kinds of entry, handled at different times:

- **Activation** -- what must be SET UP before anything runs, in the
  machine-readable `requires_` forms below. The adopting agent acts on these
  ITSELF, first, before asking anything.
- **Adaptation** -- what must be DECIDED or REWIRED, in prose. Worked through
  interactively with the user, after activation.

Activation: none. Tomorrowkit runs as published, with no external permissions
or secrets. No code in the snapshot calls an AI provider or an external API;
the interview is conducted by the agent already configured for the Mind, and
optional research uses only tools and connectors the user chooses to attach.

Adaptation:

- **The listen port is set in two places.** `8090` appears in the
  `[program:tomorrowkit]` block's `forward_port.py --url` and as the
  `TOMORROWKIT_PORT` default in `runner.py`. An adopter who needs a different
  port changes both, or sets `TOMORROWKIT_PORT` in the supervisord command and
  updates the `--url` to match.
- **Matter records are plaintext JSON.** They live under
  `data/.apps/tomorrowkit/` and follow the workspace's normal persistence and
  backup behaviour; exported ZIPs contain the same confidential material. An
  adopter working on a sensitive invention confirms the workspace's backup and
  privacy posture, uses a model account with training opt-outs enabled, and
  connects only the research tools they choose.
- **The tab talks to the chat over loopback.** Its ask-the-agent buttons post to
  the workspace UI's chat API (default `http://127.0.0.1:8000`, overridable via
  `TOMORROWKIT_CHAT_API`) using the chat agent id the bridge stamps on the matter.
  A matter created by hand in the tab has no owning chat until the agent next
  updates it. Nothing to do inside a Mind; outside one, point the variable at a
  stub or leave the buttons unused.
- **One agent, not a council.** The interview and record scoring run on the
  one agent configured for the Mind. The template does not include the
  multi-model attack and landscape roles the wider Provisionally Tomorrow Kit
  uses and must not be presented as an independent council. An adopter who
  wants adversarial review from a second model wires it through the
  workspace's normal AI integrations and records its output in the Reference
  Library as generated material, never as inventor source.

## Environment

What this template needs INSTALLED, beyond what the template already has.
Declared in `template.toml`'s `[environment]` table; an adopting mind
converges it at ITS OWN pinned apt snapshot timestamp, so package versions come
out consistent with the rest of that mind's environment rather than frozen to
whatever this publisher happened to have.

Nothing extra -- runs on the stock workspace environment.

## How to adapt it

Instructions for the NEXT agent -- the one adapting this template into a
new mind. This is the `use-template` skill's template path; in short:

1. Read this entire file first, especially "Requirements" above. There are no
   activation lines, so nothing needs to be connected before the product
   works.
2. Present the template to the user in plain, non-technical language: it
   interviews them about one invention and keeps a private record beside the
   chat; nothing leaves the Mind; it organizes and pressure-tests a working
   record and does not file anything or decide patentability.
3. Start the product immediately. Read
   `.agents/skills/tomorrowkit-provisional/SKILL.md` in full, run `uv run
   tomorrowkit-workspace list`, and either resume the existing matter or ask
   the first triage question. Do not send a patent-law lesson, a form, or a
   prompt to copy. Done for this template means the user has answered a
   question and can see the record growing in the Tomorrowkit tab.
4. Only after the first matter exists, and only if the user asks, work through
   the adaptation bullets above one at a time, in plain language, resolving
   the obvious ones yourself.
5. When done, append a dated entry to "Adaptation history" below (never
   rewrite earlier entries) and commit.

## Publication history

This template's changelog: what each published version changed. The PUBLISHER
appends one entry per version (newest last); earlier entries are never rewritten.
This is distinct from "Adaptation history" below, which is the ADOPTERS' log.

### v1 (2026-08-31) -- first publish as a v1 inspiration (`inspiration-tomorrowkit.md`) on the pre-restructure workspace tree; redesigned the next day around the conversational harvest.
### v2 (2026-09-02) -- republished in the v2 template format on the current default-workspace-template base: the app moved to `system/apps/tomorrowkit` with its own origin and the location beacon, the agent bridge accepts the revision exactly as `show` prints it, and the README carries real screenshots and an adoption section.
### v3 (2026-09-02) -- the record service's home page no longer carries the five-question orientation form or its `/api/orientation` route; it shows the resume cards and a start-in-chat panel, so the conversation is the only intake path.
### v4 (2026-09-02) -- seeds, posture, and scorecard become record data the agent writes from conversation; `next` and `advance` steer the phase marker; the tab gains a seed-portfolio pane and ask-the-agent buttons that type messages into the owning chat.

## Adaptation history

Each mind that adapts this template appends one dated entry below. Earlier
entries are never rewritten.
