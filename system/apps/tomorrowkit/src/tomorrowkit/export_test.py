import io
import json
import zipfile
from datetime import datetime, timezone

from tomorrowkit.data_types import (
    PosturePlan,
    ProvisionalPosture,
    Seed,
    SeedId,
    SeedOrigin,
    SeedRoute,
    SeedStatus,
)
from tomorrowkit.export import (
    build_export_zip_bytes,
    render_brief_markdown,
    render_decision_ledger_markdown,
    render_map_markdown,
    render_reference_library_markdown,
    render_scorecard_markdown,
    render_seed_portfolio_markdown,
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
        "seed-portfolio.md",
        "decision-ledger.md",
        "scorecard.md",
        "harvest-notes.md",
    }
    raw_record = json.loads(archive.read("matter.json"))
    assert raw_record["matter_id"] == matter.matter_id
    assert raw_record["title"] == matter.title


def test_seed_portfolio_markdown_lists_seeds_and_the_posture() -> None:
    now = datetime(2026, 9, 2, tzinfo=timezone.utc)
    matter = build_sample_matter().model_copy(
        update={
            "seeds": (
                Seed(seed_id=SeedId.generate(), label="Pressure-energised lip", mechanism="Grips harder as pressure rises.", origin=SeedOrigin.INVENTOR, status=SeedStatus.ACCEPTED, route=SeedRoute.STANDALONE, closest_art_note="Threaded collars only.", created_at=now, updated_at=now),
                Seed(seed_id=SeedId.generate(), label="Bleed groove", mechanism="Vents the first surge.", origin=SeedOrigin.MODEL, status=SeedStatus.DEFERRED, created_at=now, updated_at=now),
            ),
            "posture": PosturePlan(posture=ProvisionalPosture.LEAN_CORE_STUB, rationale="Core is settled.", approved_by_inventor=True),
        }
    )

    markdown = render_seed_portfolio_markdown(matter)

    assert "Pressure-energised lip" in markdown and "Accepted" in markdown and "Standalone" in markdown
    assert "Bleed groove" in markdown and "Deferred" in markdown and "Model proposal" in markdown
    assert "Lean-core priority stub" in markdown and "Core is settled." in markdown
    assert "approved by the inventor" in markdown.lower()


def test_export_zip_includes_the_seed_portfolio() -> None:
    archive = zipfile.ZipFile(io.BytesIO(build_export_zip_bytes(build_sample_matter())))

    assert "seed-portfolio.md" in archive.namelist()
