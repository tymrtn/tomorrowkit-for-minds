# Tomorrowkit

**One invention, one private workspace.**

Tomorrowkit is a guided provisional-patent workspace for
[Imbue Minds](https://imbue.com/product/minds). It helps an inventor develop a
rough technical idea, preserve their own reasoning, organize prior art and
other references as they work, and leave with a portable matter record.

> This is a Minds inspiration: a bootable snapshot of an app and its agent
> workflow, published so another Mind can be created from it and adapted. The
> `welcome` skill introduces the workspace on the first turn; the user works
> with the agent configured for their Mind rather than moving prompts between
> products.

Tomorrowkit is an independent community project, not an official Imbue product
and not endorsed by Imbue.

![Tomorrowkit orientation](docs/images/orientation.png)

![Tomorrowkit matter workspace](docs/images/matter-workspace.png)

## The experience

A new Mind begins by asking what the inventor wants to work on. It creates one
matter and then maintains two synchronized surfaces:

- **The Mind's conversation** is where the invention harvest happens. The
  active agent asks questions, researches with tools the user has approved,
  tests assumptions, and proposes updates.
- **The Tomorrowkit tab** is the visible working record: Matter Home,
  Invention Brief, Harvesting Room, Invention Map, Reference Library, Decision
  Ledger, provisional-stage scorecards, and export.

The user never has to copy a canned prompt into another chat. The agent reads
and updates the same validated local record displayed by the app.

## Why Minds

Minds gives Tomorrowkit the properties that matter here: a reusable template
that can become the user's own workspace; a privacy-oriented environment that
can run locally or through Imbue's cloud; persistent project context; and an
agent system that is not inherently limited to one model vendor.

Tomorrowkit therefore does not embed a provider key or call a hard-coded model
API. It supplies the invention workflow and artifacts to whichever agent is
configured for the Mind. The included workspace currently follows Minds'
default agent setup; mngr's agent/provider architecture leaves room for Claude,
Codex, Gemini, and other integrations. A genuine multi-model Council Room is a
future extension and is not simulated in this release.

## What it includes

- Plain-English orientation to provisional-stage patent work
- One matter per Mind
- An editable invention brief in the inventor's language
- Four guided checkpoints: intake, prospecting, disclosure development, and
  adversarial review
- An Invention Map for mechanisms, flows, alternatives, and open questions
- A living Reference Library for patents, papers, products, standards, and
  research leads, including provenance and verification state
- A Decision Ledger for inventor-approved choices
- Separate IVS and PAS review lenses, never collapsed into one magic score
- Portable Markdown, JSON, and ZIP exports

The first version deliberately excludes formal patent figures, filing
automation, PCT/non-provisional prosecution scoring, and claims that a single
agent constitutes a council.

## How it works

Three parts are joined inside the same Mind:

1. **The `tomorrowkit-provisional` skill does the thinking.** It conducts the
   interview, preserves the distinction between inventor statements and model
   suggestions, grows the reference library, and identifies gaps.
2. **The Tomorrowkit web service is the visual surface.** It runs as a local
   service registered with Minds and appears at `/service/tomorrowkit/`.
3. **The `tomorrowkit-workspace` command is the bridge.** It gives the agent a
   deterministic, schema-validated way to create, inspect, and revision-check
   updates to the record. References enter as unverified leads by default.

Matter data lives under `runtime/tomorrowkit/` in the booted Mind and is covered
by the workspace's normal persistence and backup behavior.

## Adopting this inspiration

Create a Mind from this repository. On its first turn the `welcome` skill reads
[`inspiration-tomorrowkit.md`](inspiration-tomorrowkit.md), explains the
workspace, and asks for the core idea in the inventor's own words. No connector
or additional API key is required to begin.

The manifest is the adoption contract: it explains prerequisites, first-run
behavior, deliberate limitations, and how the agent should adapt the snapshot.

## Development

The bootable snapshot is based on Imbue's default persistent-workspace template.
The Tomorrowkit-specific pieces are:

- `inspiration-tomorrowkit.md` and `inspiration-tomorrowkit.svg`
- `.agents/skills/welcome`
- `.agents/skills/tomorrowkit-provisional`
- `libs/tomorrowkit`
- the `[program:tomorrowkit]` entry in `supervisord.conf`

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

Then open `http://127.0.0.1:8090`.

## Privacy and legal boundary

Matter records are local plaintext JSON inside the Mind's runtime directory.
Use the privacy mode and model account appropriate for the sensitivity of the
work, enable available training opt-outs, and connect only services the user
chooses. Read [SECURITY.md](SECURITY.md) before exposing the service outside
Minds; it binds to localhost and has no standalone authentication layer.

Tomorrowkit organizes an inventor-controlled working record. It does not file
applications, determine inventorship, provide legal advice, or guarantee that
a disclosure supports a later claim.

## License

Tomorrowkit-specific code and documentation are available under the
[Fair Core License 1.0 with an MIT future license](LICENSE.md). Noncompeting
use is permitted immediately; each version becomes available under MIT two
years after release. The bootable Minds workspace also contains third-party
components under their own licenses. Bundled font notices are collected in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
