# Tomorrowkit

**Tell Tomorrowkit how the invention works. Watch the record take shape.**

Tomorrowkit is a private, conversational invention-harvest workspace for
[Imbue Minds](https://imbue.com/product/minds). It helps a solo inventor move
from a rough idea to a source-aware invention record, a portfolio of technical
seeds, a living reference library, an inventor-approved filing strategy, and a
portable handoff.

Tomorrowkit is an independent community project, not an official Imbue product
and not endorsed by Imbue.

## The product is the conversation

The inventor works in chat. Tomorrowkit asks one useful question at a time,
adapts to each answer, and updates the matter after every meaningful exchange.
The Tomorrowkit tab opens beside the conversation and shows the record taking
shape: brief, map, references, decisions, score lenses, and export.

The tab is a review and correction surface. A user should not have to complete
a monster intake form, populate a blank brief, administer checkpoints, copy a
prompt, or manually keep the record synchronized.

On a new Mind, Tomorrowkit begins with five short questions, asked one at a
time. Every answer immediately explains the patent concept that makes the
choice relevant, so orientation happens through the user's own situation
instead of a front-loaded lesson:

1. Is the invention in the inventor's head, documented or built, in a draft
   provisional, or already filed?
2. Is it private, shared confidentially, maybe public, or already public or
   commercial?
3. What should the patent work accomplish?
4. What source material already exists?
5. How should Tomorrowkit work with the inventor?

After the first answered category, it creates an untitled matter and opens the
live record so every later answer is preserved. It skips categories already
answered naturally. Once the five categories are covered, it begins Source Lock
and the technical interview; the first mechanism answers supply a real working
title. On a returning Mind, it reads the existing matter and resumes at the next
material gap.

## The invention workflow

Tomorrowkit follows a gated conversational state machine:

```text
Welcome → Triage quiz → Source lock → Objective lock → Core mechanism
→ Seed expansion → Seed assay → Terrain selection → Provisional posture
→ Disclosure build → Attack/repair → Ready/handoff
```

This is not a fixed questionnaire. The next question comes from the inventor's
last answer, the current gate, and the most important unresolved gap.

### Source before expansion

Tomorrowkit first separates:

- inventor material that existed by the relevant date;
- inventor notes or improvements added later;
- public and third-party references;
- model-generated proposals and analysis; and
- research leads or public references needing later review.

It records contributors, ownership concerns, disclosures, filings, and known
deadlines. Model output never silently becomes earlier inventor source.

### Objective before optimization

The inventor confirms what the patent work is for, who or what matters, the
commercial or public-benefit control point, what should remain private,
realistic timing and budget, and 12- and 24-month success. Tomorrowkit records
the working style and human gates instead of optimizing a generic patent score.

### Mechanism before patent prose

The interview moves from the product pitch into the technical operation:
actors, components, relationships, inputs and outputs, a complete operating
cycle, the mechanism that causes the result, evidence and testing, constraints,
failures, rejected routes, and alternatives. The brief grows in the inventor's
own language while unknowns remain visibly unknown.

### Multiple seeds before a filing thesis

Tomorrowkit harvests several distinct technical mechanisms or seed families
before drafting. Each model-proposed seed is presented as a proposal for the
inventor to accept, edit, reject, or defer. Confirmed seeds receive preliminary
closest-art and design-around pressure and are compared as standalone, combine,
later filing, defer, or no-file routes.

The inventor selects the terrain. A long draft produced before this portfolio
gate is not treated as progress.

### An explicit provisional posture

After terrain selection, the inventor chooses one of three strategies:

- **Lean-core priority stub:** protect the essential core and workable
  implementation while intentionally withholding nonessential know-how.
- **Disclosure reservoir:** preserve the widest technically supported set of
  future paths.
- **Layered provisionals:** file planned layers over time, each with its own
  date and the earliest conversion deadline still controlling.

Tomorrowkit records what needs the first date, what stays withheld or staged,
disclosure and foreign-filing constraints, the next filing trigger, important
dates, and the inventor's approval. The agent may recommend a posture; it does
not choose one silently.

## The living record

The record includes:

- an evolving invention brief;
- known facts, uncertainties, and the next action;
- source labels and provenance;
- a seed portfolio and inventor dispositions;
- a visual Invention Map for thinking, not formal patent drawings;
- a Reference Library of inventor materials, patents, papers, products,
  standards, web sources, and research leads;
- a Decision Ledger for objective, terrain, embodiment, deferral, disclosure,
  and suggestion choices;
- separate provisional-stage score lenses; and
- Markdown, JSON, and ZIP export.

New research enters as a lead until reviewed against the source. “No result
found” is not treated as proof of novelty.

## Score lenses

Tomorrowkit keeps three questions separate:

- **IVS — Invention Value Score:** does the inventor-approved terrain appear
  worth pursuing? Available dimensions can be assessed during seed work, with
  evidence and coverage visible.
- **PAS — Priority Asset Score:** does a complete provisional candidate or filed
  provisional actually capture that terrain? It remains unassessed before that
  record exists.
- **PSS — Prosecution Survival Score:** would an actual later claim set survive
  prosecution and challenge? It requires a non-provisional or international
  claim set and is outside this provisional experience.

The lenses are never averaged into one magic score, and a score cannot quietly
shrink the terrain the inventor selected.

## Human control and AI provenance

In a directed inventor-and-model session, Tomorrowkit starts with the directing
human as the inventor and preserves their problem framing, constraints,
steering, understanding, selection, modification, integration, and adoption of
the settled solution. It does not run a word-by-word origin audit or discard a
supported concept merely because a model proposed a version of it first.

Model output alone is not inventor source or proof that the inventor possesses
the solution. Important proposals stay distinguishable until the inventor
understands and disposes of them.

The inventor decides objectives, source classifications, contributor and
ownership facts, seed and terrain selection, disclosure posture, withheld
matter, fight/narrow/park/split/defer/drop choices, publication, filing route,
spend, signatures, certifications, payment, and final submission.

## How it works inside Minds

Three parts share the same local matter:

1. **The `tomorrowkit-provisional` skill** conducts the adaptive interview and
   enforces the workflow gates.
2. **The Tomorrowkit service** displays the living record at
   `/service/tomorrowkit/`.
3. **The `tomorrowkit-workspace` command** lets the agent create, inspect, and
   revision-check updates without asking the user to edit files or move prompts.

After a matter is created or resumed, the agent opens the service beside chat
with:

```bash
python3 scripts/layout.py open tomorrowkit
```

Matter data lives under `runtime/tomorrowkit/` in the booted Mind and follows
the workspace's normal persistence and backup behavior.

## Why Minds

Minds provides a reusable private workspace, persistent context, and a model-
agnostic agent environment. Tomorrowkit does not embed a provider key or bind
the workflow to one model vendor. Optional research uses only tools and
connectors the user chooses.

One configured agent can perform structured drafting, research, and attack
roles, but this release does not pretend that one agent is an independent
multi-model council.

## Boundaries

Tomorrowkit organizes and pressure-tests an inventor-controlled working record.
It does not determine patentability, guarantee priority, provide a legal
conclusion, file applications, create filing-standard drawings, sign forms,
certify entity status, spend money, or submit anything to a patent office.

The initial inspiration focuses on provisional-stage work. Formal non-
provisional/international claims, prosecution scoring, filing automation, and a
genuine independent council belong to later, separately authorized workflows.

Matter records are local plaintext JSON. Use a privacy mode and model account
appropriate for sensitive work, enable available training opt-outs, and connect
only services the inventor chooses. Read [SECURITY.md](SECURITY.md) before
exposing the service outside Minds; it binds to localhost and has no standalone
authentication layer.

## Development

The Tomorrowkit-specific pieces are:

- `inspiration-tomorrowkit.md` and `inspiration-tomorrowkit.svg`;
- `.agents/skills/welcome`;
- `.agents/skills/tomorrowkit-provisional`;
- `libs/tomorrowkit`; and
- the `[program:tomorrowkit]` entry in `supervisord.conf`.

Install the workspace and run the Tomorrowkit tests:

```bash
uv sync --all-packages
uv run pytest libs/tomorrowkit
uv run pyright libs/tomorrowkit/src/tomorrowkit
```

For service-only development:

```bash
TOMORROWKIT_DATA_DIR=/tmp/tomorrowkit-data uv run tomorrowkit
```

Then open `http://127.0.0.1:8090` to inspect the record surface. The full
product experience runs in a Mind because the conversation is the primary
surface.

## License

Tomorrowkit-specific code and documentation are available under the
[Fair Core License 1.0 with an MIT future license](LICENSE.md). Noncompeting use
is permitted immediately; each version becomes available under MIT two years
after release. Bundled third-party components remain under their own licenses;
font notices are collected in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
