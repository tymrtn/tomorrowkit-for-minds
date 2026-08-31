---
title: Tomorrowkit
description: A private, guided provisional-patent workspace that helps an inventor develop an idea, preserve human decisions, and build a living reference library with the agent they choose in Minds.
thumbnail: inspiration-tomorrowkit.svg
---

# Tomorrowkit

This is the manifest for the **Tomorrowkit** Minds inspiration (slug:
`tomorrowkit`). A new Mind created from this repository must read this document
on its first turn and adapt the workspace to one invention.

## What it is

Tomorrowkit turns one Mind into a private working environment for one
invention. The Mind's configured agent conducts the conversation; the
Tomorrowkit skill supplies the provisional-stage workflow; and the Tomorrowkit
web service provides the visual record: orientation, invention brief,
harvesting checkpoints, invention map, reference library, decision ledger,
provisional scorecards, and export.

The application does not embed an API key or bind the workflow to a model
vendor. It uses the agent selected for the Mind. A user may begin with the
default agent and later extend the Mind with other mngr-supported agents or
providers. A future Council Room may reconcile several independent agents, but
this version never simulates a council with one model.

## How it works

Three pieces work together:

- `.agents/skills/tomorrowkit-provisional/SKILL.md` is the workflow. It tells
  the active Minds agent how to interview the inventor, preserve attribution,
  prospect references, deepen the disclosure, and identify gaps.
- `libs/tomorrowkit` is the visual service. It stores each matter as a local
  JSON record under `runtime/tomorrowkit/`, serves the app at
  `/service/tomorrowkit/`, and exports portable Markdown and JSON.
- `tomorrowkit-workspace` is the validated bridge between them. The agent uses
  it to create, read, and update matter records. It rejects stale writes,
  validates every update against the matter schema, and marks new references
  as unverified leads by default.

The user should never have to copy a prompt between the web app and a chat.
They talk to the Mind. The agent reads and updates the same record displayed by
the Tomorrowkit tab.

## Prerequisites

The initial inspiration has no required connector, external account, or API
secret. It runs with the agent and privacy mode the user chose for their Mind.
Optional research connectors can be added later with the user's permission.

## How to adapt it

Instructions for the agent in a newly created Mind:

1. Read this entire manifest and the `tomorrowkit-provisional` skill.
2. Explain in plain language that this Mind will become a private workspace for
   one invention. Make clear that Tomorrowkit organizes the inventor's record;
   it does not file an application or determine legal rights.
3. Ask for the core idea in the inventor's own words. Then ask only the
   minimum follow-up questions needed to create the matter: working title,
   present stage, known public-disclosure or filing dates, and immediate goal.
   Ask one question at a time.
4. Create the matter with `tomorrowkit-workspace create`, then tell the user
   the Tomorrowkit tab is ready. Do not ask them to edit JSON or copy prompts.
5. Continue the harvest in the Mind's conversation. After each meaningful
   exchange, use `tomorrowkit-workspace show` and a revision-checked patch to
   update the brief, checkpoint notes, reference library, decisions, and next
   action.
6. Ask before treating an inference as an inventor-approved fact. Preserve the
   user's words and keep model suggestions visibly distinct.
7. When adapting the workflow or interface, record the change in the git
   history. Do not silently alter the user's matter or apply proposed rules
   without confirmation.

## Holes and deliberate boundaries

- **No multi-model council yet.** This version uses the active Mind agent. A
  genuine council needs independent contexts, attributable outputs, and an
  explicit reconciliation step.
- **Provisional stage only.** PCT, non-provisional prosecution scoring, formal
  claims strategy, and formal patent figures are outside this inspiration.
- **No filing automation.** Export produces a working record, not a ready-to-
  file application or a legal conclusion.
- **Reference discovery depends on available tools.** The library works
  without connectors. Any patent, paper, web, or account connector must be
  user-approved; new results enter as leads until reviewed.
- **The Invention Map is a thinking surface.** It is not a formal patent-
  drawing editor.

## Adaptation history

Each Mind that materially adapts this inspiration should append a dated entry
below without rewriting earlier entries.
