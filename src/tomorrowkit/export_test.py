import io
import json
import zipfile

from tomorrowkit.export import (
    build_export_zip_bytes,
    render_brief_markdown,
    render_decision_ledger_markdown,
    render_map_markdown,
    render_reference_library_markdown,
    render_scorecard_markdown,
)
from tomorrowkit.testing import build_sample_matter


def test_brief_markdown_contains_title_stage_and_dates() -> None:
    matter = build_sample_matter()

    markdown = render_brief_markdown(matter)

    assert "Self-sealing irrigation coupler" in markdown
    assert "Early idea" in markdown
    assert "Farm demo" in markdown
    assert "2026-03-14" in markdown


def test_map_markdown_writes_out_nodes_and_connections() -> None:
    matter = build_sample_matter()

    markdown = render_map_markdown(matter)

    assert "Compression ring" in markdown
    assert "Material fatigue?" in markdown
    assert "raises" in markdown
    assert "->" in markdown


def test_reference_library_markdown_includes_entry_metadata() -> None:
    matter = build_sample_matter()

    markdown = render_reference_library_markdown(matter)

    assert "US 9,999,999 coupler patent" in markdown
    assert "Patent publication" in markdown
    assert "Needs verification" in markdown
    assert "coupler, sealing" in markdown
    assert "not a filed" in markdown


def test_decision_ledger_markdown_includes_decisions() -> None:
    matter = build_sample_matter()

    markdown = render_decision_ledger_markdown(matter)

    assert "Lead with the compression-ring embodiment" in markdown
    assert "Embodiment choice" in markdown


def test_scorecard_markdown_keeps_both_lenses_separate() -> None:
    matter = build_sample_matter()

    markdown = render_scorecard_markdown(matter)

    assert "IVS -- Invention Value Score" in markdown
    assert "PAS -- Priority Asset Score" in markdown
    assert "not independent" in markdown


def test_export_zip_contains_every_artifact_and_the_raw_record() -> None:
    matter = build_sample_matter()

    zip_bytes = build_export_zip_bytes(matter)
    archive = zipfile.ZipFile(io.BytesIO(zip_bytes))

    assert set(archive.namelist()) == {
        "README.md",
        "matter.json",
        "invention-brief.md",
        "invention-map.md",
        "reference-library.md",
        "decision-ledger.md",
        "scorecard.md",
        "harvest-notes.md",
    }
    raw_record = json.loads(archive.read("matter.json"))
    assert raw_record["matter_id"] == matter.matter_id
    assert raw_record["title"] == matter.title
