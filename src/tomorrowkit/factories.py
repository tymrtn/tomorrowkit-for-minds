from datetime import datetime, timezone
from typing import Final

from imbue.imbue_common.pure import pure

from tomorrowkit.data_types import (
    HarvestCheckpoint,
    MatterDocument,
    MatterId,
    MatterIntake,
)

_INTAKE_PROMPT: Final[str] = """\
I am working on a provisional patent record for my invention. Help me run an invention intake interview.

Ask me one question at a time, adapting to my answers. Cover: the problem and who has it; how my \
invention works, step by step; what makes it different from the obvious way of doing it; every variation \
or alternative version I have considered; what I have actually built or tested so far; and any public \
demos, sales, publications, or disclosures I have already made (with dates as best I remember).

Keep my own words. Do not rewrite my descriptions into patent language. At the end, give me a summary \
organized as: problem, mechanism, intended result, alternatives, open questions -- so I can paste each \
part into the matching section of my invention brief."""

_PROSPECTING_PROMPT: Final[str] = """\
I am building a reference library for my invention's provisional patent record. Help me search for prior \
art and related work.

Based on my invention brief (included below), suggest search terms and look for: existing patents \
and patent applications, academic papers, commercial products, and technical standards that are close to \
my idea. For each thing you find, give me: a title, a citation or stable link, what kind of source it is, \
one plain-English sentence on how it relates to my invention (does it support my thinking, contradict it, \
suggest a design-around, or just need verification?), and its date if known.

Mark everything you find as a lead -- I will review and verify entries myself before I rely on them."""

_DRAFTING_PROMPT: Final[str] = """\
I am developing the disclosure for my invention's provisional patent record. Using my invention brief and \
invention map (included below), help me make the description complete enough that someone skilled \
in this field could build the invention.

Walk through each component and step and ask me about anything that is vague: exact mechanisms, ranges, \
materials, orderings, failure handling, and alternatives. Push me to describe every variation I would not \
want a competitor to use freely. Flag places where I say 'somehow' or skip a step. Keep the output \
organized by the sections of my brief, and clearly separate what I told you from what you inferred, so I \
can review and approve each part."""

_ADVERSARIAL_PROMPT: Final[str] = """\
Act as a skeptical reviewer of my invention disclosure. My invention brief, map summary, and \
reference library are included below.

Attack the record: What is missing that a patent attorney would ask for? Which claims of novelty look weak \
against the references I have collected? Where is the description too vague to support what I care about? \
What obvious variations have I failed to describe? What evidence am I assuming but not actually holding?

Give me a prioritized list of gaps, each with a plain-English explanation of why it matters and what would \
close it. Do not soften the review -- I want the problems found now, not after filing."""

_DEFAULT_HARVEST_CHECKPOINTS: Final[tuple[tuple[str, str, str, str], ...]] = (
    (
        "intake",
        "Intake interview",
        "Get the whole invention out of your head and into the brief, in your own words.",
        _INTAKE_PROMPT,
    ),
    (
        "prospecting",
        "Prior-art prospecting",
        "Search for patents, papers, and products near your idea and grow the reference library.",
        _PROSPECTING_PROMPT,
    ),
    (
        "drafting",
        "Disclosure drafting",
        "Deepen the description until someone skilled in the field could build it.",
        _DRAFTING_PROMPT,
    ),
    (
        "adversarial",
        "Adversarial review",
        "Have your agent attack the record and list the gaps before they become problems.",
        _ADVERSARIAL_PROMPT,
    ),
)


@pure
def build_default_harvest_checkpoints() -> tuple[HarvestCheckpoint, ...]:
    return tuple(
        HarvestCheckpoint(
            checkpoint_id=checkpoint_id,
            name=name,
            purpose=purpose,
            agent_prompt=agent_prompt,
        )
        for checkpoint_id, name, purpose, agent_prompt in _DEFAULT_HARVEST_CHECKPOINTS
    )


def create_matter_from_intake(intake: MatterIntake) -> MatterDocument:
    now = datetime.now(timezone.utc)
    return MatterDocument(
        matter_id=MatterId.generate(),
        created_at=now,
        updated_at=now,
        title=intake.title,
        problem_summary=intake.problem_summary,
        stage=intake.stage,
        goal=intake.goal,
        theme=intake.theme,
        known_dates=intake.known_dates,
        harvest=build_default_harvest_checkpoints(),
    )
