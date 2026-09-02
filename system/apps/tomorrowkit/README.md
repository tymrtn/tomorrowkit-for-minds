# tomorrowkit

The Tomorrowkit record service and agent bridge: a Flask app that renders one
invention matter (brief, map, references, decisions, score lenses, export) as a
tab beside the chat, and the `tomorrowkit-workspace` console script the agent
uses to list, create, read, and apply revision-checked patches to that matter.

Matter data lives under `data/.apps/tomorrowkit/` (override with
`TOMORROWKIT_DATA_DIR`); the service listens on `127.0.0.1:8090` (override with
`TOMORROWKIT_PORT`). The interview that drives it is
`.agents/skills/tomorrowkit-provisional`; the product contract is `template.md`
at the repo root.
