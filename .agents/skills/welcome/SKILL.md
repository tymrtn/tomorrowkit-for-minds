---
name: welcome
description: Start or resume the conversational Tomorrowkit invention workflow when a user opens a Mind created from this inspiration.
---

# Welcome the user to Tomorrowkit

Tomorrowkit is a guided conversation with a living matter record beside it. The
chat is the product. The Tomorrowkit tab is the record the conversation builds;
it is not an intake form the user must complete.

On the first turn:

1. Read `inspiration-tomorrowkit.md` and
   `.agents/skills/tomorrowkit-provisional/SKILL.md` in full.
2. Run `uv run tomorrowkit-workspace list`.
3. If a matter exists, read it with `uv run tomorrowkit-workspace show
   <matter_id>`, run `python3 scripts/layout.py open tomorrowkit`, give a
   one-sentence recap of where the work stopped, and ask the single next useful
   question required by the workflow state.
4. If no matter exists, begin the five-category triage quiz. Welcome the user in
   one sentence and explain that their answers will establish a private
   starting point before the technical interview. If the opening message has
   already answered one or more categories, acknowledge and retain those
   answers instead of repeating a question. Otherwise ask question one:

   **“Where is this invention today: mostly in your head, captured in notes or a
   build, in a draft provisional, or already filed?”**

After the first answered category, follow the `tomorrowkit-provisional` skill
to create the matter and open its record beside chat. Do not send a patent-law
lesson, a suggestions menu, a multi-field intake, or a prompt for the user to
copy. Do not ask several questions in one message. The `tomorrowkit-provisional`
skill owns every subsequent turn, record update, and human decision gate.
