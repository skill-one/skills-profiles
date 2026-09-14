"""Tests for per-prompt markdown output rendering and the on-disk layout."""

import pytest

from skills_profiles.data import load_skills
from skills_profiles.generate import run_all
from skills_profiles.llm import FakeLLM
from skills_profiles.models import Domain
from skills_profiles.outputs import (
    invalidate,
    load_hashes,
    load_index,
    skill_result_dir,
    write_index,
)


@pytest.fixture
async def results(settings, prompt_set):
    skills = load_skills(settings)
    return await run_all(FakeLLM(), settings, skills, prompt_set)


def test_one_json_in_skill_dir_and_one_md_in_subdir(settings, results):
    for record in results:
        skill_id = record["skill"]["id"]
        skill_dir = settings.output_dir / "skills" / skill_id.replace(":", "_")
        stems_json = {p.stem for p in skill_dir.glob("*.json")}
        stems_md = {p.stem for p in (skill_dir / "md").glob("*.md")}
        assert stems_json == set(record["intros"])
        assert stems_md == set(record["intros"])
        assert not list(skill_dir.glob("*.md"))  # json stays uncluttered


def test_skill_output_files_render_fields(settings, results):
    record = results[0]
    skill_id = record["skill"]["id"]
    md_dir = settings.output_dir / "skills" / skill_id.replace(":", "_") / "md"
    intro = record["intros"]

    scenario = (md_dir / "scenario.md").read_text(encoding="utf-8")
    assert skill_id.rsplit("/", 1)[-1] in scenario
    assert intro["scenario"]["text"] in scenario

    taglines = (md_dir / "tagline.md").read_text(encoding="utf-8")
    for tagline in intro["tagline"]["taglines"]:
        assert f"- {tagline}" in taglines

    whitebox = (md_dir / "whitebox.md").read_text(encoding="utf-8")
    for step in intro["whitebox"]["execution_flow"]:
        assert f"- {step}" in whitebox

    blackbox = (md_dir / "blackbox.md").read_text(encoding="utf-8")
    for pair in intro["blackbox"]["input_output"]:
        assert f"- input: {pair['input']}, output: {pair['output']}" in blackbox

    domain_md = (md_dir / "domain.md").read_text(encoding="utf-8")
    assert Domain.display(intro["domain"]["domain"]) in domain_md  # emoji-prefixed

    persona_md = (md_dir / "persona.md").read_text(encoding="utf-8")
    for field in ("tool", "pitch"):
        assert f"**{field}**: {intro['persona'][field]}" in persona_md

    comments_md = (md_dir / "comments.md").read_text(encoding="utf-8")
    for c in intro["comments"]["comments"]:
        assert f"- user: {c['user']}, category: {c['category']}, comment: {c['comment']}" in comments_md


def test_invalidate_one_prompt_removes_only_it(settings, results):
    skill_id = results[0]["skill"]["id"]
    skill_dir = skill_result_dir(settings, skill_id)

    assert invalidate(settings, [skill_id], {"tagline"}) == 1
    assert not (skill_dir / "tagline.json").exists()
    assert not (skill_dir / "md" / "tagline.md").exists()
    # siblings and the hash record survive a partial invalidation
    assert (skill_dir / "domain.json").exists()
    assert (skill_dir / "md" / "domain.md").exists()
    assert skill_id in load_hashes(settings)


def test_invalidate_assets_only_keeps_the_output_drops_its_asset(settings, results):
    """assets-only removal deletes just the rendered asset a prompt owns; the
    json, its markdown and the hash record all stay, so the next run re-renders
    the asset from the recipe already on disk."""
    skill_id = results[0]["skill"]["id"]
    skill_dir = skill_result_dir(settings, skill_id)
    (skill_dir / "cover.png").write_bytes(b"png")

    assert invalidate(settings, [skill_id], {"cover"}, assets_only=True) == 1
    assert not (skill_dir / "cover.png").exists()
    assert (skill_dir / "cover.json").exists()
    assert (skill_dir / "md" / "cover.md").exists()
    assert skill_id in load_hashes(settings)


def test_invalidate_whole_skill_drops_it_from_the_hashes(settings, results):
    skill_id = results[0]["skill"]["id"]
    skill_dir = skill_result_dir(settings, skill_id)

    assert invalidate(settings, [skill_id]) == len(results[0]["intros"])
    assert not skill_dir.exists()
    assert skill_id not in load_hashes(settings)


def test_invalidate_one_prompt_for_every_skill(settings, results):
    assert invalidate(settings, prompt_ids={"whitebox"}) == len(results)
    for record in results:
        skill_dir = skill_result_dir(settings, record["skill"]["id"])
        assert not (skill_dir / "whitebox.json").exists()
        assert (skill_dir / "domain.json").exists()
    assert set(load_hashes(settings)) == {r["skill"]["id"] for r in results}


def test_index_aggregates_domain_and_persona(settings, results):
    """skills.jsonl folds each skill's domain and persona outputs into its line,
    with keys in the canonical order (id, hash, domain, persona)."""
    index = load_index(settings)
    for record in results:
        line = index[record["skill"]["id"]]
        assert list(line) == ["id", "hash", "domain", "persona"]
        assert line["hash"] == record["skill"]["hash"]
        assert line["domain"] == record["intros"]["domain"]
        assert line["persona"] == record["intros"]["persona"]


def test_invalidate_clears_the_aggregated_copy(settings, results):
    """Dropping a skill's domain json also clears the aggregated copy in the
    index line; persona and the hash survive."""
    skill_id = results[0]["skill"]["id"]
    invalidate(settings, [skill_id], {"domain"})
    line = load_index(settings)[skill_id]
    assert "domain" not in line
    assert line["persona"] == results[0]["intros"]["persona"]
    assert line["hash"] == results[0]["skill"]["hash"]


async def test_partial_run_aggregates_only_what_it_generated(settings, results, prompt_set):
    """After a tagline-only refill the line is back on record with a fresh hash
    but carries no domain/persona until those exist on disk again."""
    skill_id = results[0]["skill"]["id"]
    invalidate(settings, [skill_id])
    await run_all(FakeLLM(), settings, load_skills(settings)[:1], prompt_set,
                  only={"tagline"})
    line = load_index(settings)[skill_id]
    assert line["hash"] == results[0]["skill"]["hash"]
    assert "domain" not in line and "persona" not in line


def test_index_rewrite_heals_legacy_lines(settings, results):
    """A line written before aggregation existed (id + hash only) is re-derived
    from disk on the next index rewrite, instead of staying stale forever."""
    record = results[0]
    skill_id = record["skill"]["id"]
    write_index(settings, {skill_id: {"id": skill_id, "hash": record["skill"]["hash"]}})
    line = load_index(settings)[skill_id]
    assert line["hash"] == record["skill"]["hash"]
    assert line["domain"] == record["intros"]["domain"]
    assert line["persona"] == record["intros"]["persona"]
