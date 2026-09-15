"""Tests for DAG execution, file-based resume and end-to-end generation."""

import asyncio
import json

import pytest
from conftest import FailingForAlpha

from skills_profiles.data import load_skills, skill_md_path
from skills_profiles.generate import (
    RunStats,
    coverage,
    run_all,
    run_one,
    select_skills,
)
from skills_profiles.images import FakeImages, cover_needed, run_covers
from skills_profiles.llm import FakeLLM, RateLimitedLLM
from skills_profiles.outputs import (
    index_path,
    invalidate,
    load_hashes,
    prompt_result_path,
    skill_result_dir,
)
from skills_profiles.prompts import load_prompt_set


async def complete(settings, prompt_set, skills) -> None:
    """Take the skills all the way: text pass, then their missing covers."""
    await run_all(FakeLLM(), settings, skills, prompt_set)
    pending = [s for s in skills if cover_needed(settings, s.id)]
    if pending:
        await run_covers(FakeImages(), settings, pending)


class CountingLLM:
    """Wraps a LLM and counts how many times it was actually called."""

    def __init__(self, inner):
        self.inner = inner
        self.calls = 0

    async def create(self, response_model=None, messages=None, **kwargs):
        self.calls += 1
        return await self.inner.create(response_model, messages, **kwargs)


class ConcurrencyTrackingLLM:
    """Wraps a LLM and tracks the peak number of in-flight calls.

    A short sleep makes each call actually suspend, so overlapping calls show
    up in `peak` even though the fake inner LLM returns instantly.
    """

    def __init__(self, inner):
        self.inner = inner
        self.active = 0
        self.peak = 0

    async def create(self, response_model=None, messages=None, **kwargs):
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(0.01)
            return await self.inner.create(response_model, messages, **kwargs)
        finally:
            self.active -= 1


def stored_outputs(settings, skill_id: str) -> dict:
    """All per-prompt json outputs stored on disk for one skill."""
    skill_dir = skill_result_dir(settings, skill_id)
    return {
        p.stem: json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(skill_dir.glob("*.json"))
    }


async def test_full_run_produces_all_prompt_outputs(settings, prompt_set):
    skill = load_skills(settings)[0]
    record, _ = await run_one(FakeLLM(), settings, prompt_set, skill)
    assert set(record["intros"]) == set(prompt_set.by_id)


async def test_existing_results_skip_llm_calls(settings, prompt_set):
    skills = load_skills(settings)
    prompts = len(prompt_set.by_id)

    first = CountingLLM(FakeLLM())
    await run_all(first, settings, skills, prompt_set)
    assert first.calls == 4 * prompts  # every skill runs every prompt once

    second = CountingLLM(FakeLLM())
    results = await run_all(second, settings, skills, prompt_set)
    assert second.calls == 0  # per-prompt jsons on disk short-circuit the LLM
    assert len(results) == 4


async def test_cached_run_is_untouched_until_invalidated(settings, prompt_set):
    """Nothing regenerates until the cache is dropped: `invalidate` is the only
    way to make a run redo work."""
    skills = load_skills(settings)
    prompts = len(prompt_set.by_id)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    cached = CountingLLM(FakeLLM())
    results = await run_all(cached, settings, skills, prompt_set)
    assert cached.calls == 0
    assert len(results) == 4

    assert invalidate(settings) == 4 * prompts  # every cached output of every skill
    assert load_hashes(settings) == {}  # emptied skills drop out of the record

    forced = CountingLLM(FakeLLM())
    results = await run_all(forced, settings, skills, prompt_set)
    assert forced.calls == 4 * prompts
    assert len(results) == 4


async def test_limit_skips_cached_skills_without_spending_the_budget(settings, prompt_set):
    """`--limit` bounds the skills that generate: cached ones are skipped for free,
    so repeated runs keep moving down the install-ordered list."""
    skills = load_skills(settings)
    await complete(settings, prompt_set, skills[:2])

    # Alpha and Beta are complete: the budget of 2 goes to Gamma and Hotel
    picked = select_skills(settings, prompt_set, skills, limit=2)
    assert [s.id for s in picked] == [skills[2].id, skills[3].id]

    # nothing left to do
    await complete(settings, prompt_set, skills[2:])
    assert select_skills(settings, prompt_set, skills, limit=2) == []


async def test_limit_counts_a_missing_cover_as_work(settings, prompt_set):
    """`limit N` means N complete skills: a skill whose text is all cached but
    whose cover.png has not been drawn yet spends the budget too."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills[:2], prompt_set)  # text + recipes, no covers

    picked = select_skills(settings, prompt_set, skills, limit=2)
    assert [s.id for s in picked] == [skills[0].id, skills[1].id], \
        "alpha and beta owe their pictures: they spend the budget before gamma"

    await complete(settings, prompt_set, skills[:1])
    picked = select_skills(settings, prompt_set, skills, limit=2)
    assert [s.id for s in picked] == [skills[1].id, skills[2].id], \
        "alpha is complete now, beta still owes its picture"


async def test_limit_zero_selects_every_skill(settings, prompt_set):
    skills = load_skills(settings)
    assert select_skills(settings, prompt_set, skills, limit=0) == skills


async def test_limit_skips_skills_without_skill_md(settings, prompt_set):
    """A skill the snapshot has no SKILL.md for can never generate: selection
    passes it over, so it never sits at the head of the list burning budget."""
    skills = load_skills(settings)
    skill_md_path(settings, skills[0]).unlink()

    picked = select_skills(settings, prompt_set, skills, limit=1)
    assert [s.id for s in picked] == [skills[1].id]

    assert select_skills(settings, prompt_set, skills, limit=0) == skills[1:]


async def test_limit_defaults_to_settings(settings, prompt_set):
    skills = load_skills(settings)
    settings.limit = 1
    assert len(select_skills(settings, prompt_set, skills)) == 1


async def test_limit_respects_the_prompt_selection(settings, prompt_set):
    """With `only`, a skill counts as cached when the selected prompts are cached."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills[:1], prompt_set, only={"tagline"})

    # Alpha's tagline is cached, so it does not spend the budget
    picked = select_skills(settings, prompt_set, skills, only={"tagline"}, limit=1)
    assert [s.id for s in picked] == [skills[1].id]

    # a prompt Alpha never generated still makes it a target
    picked = select_skills(settings, prompt_set, skills, only={"domain"}, limit=1)
    assert [s.id for s in picked] == [skills[0].id]


async def test_hashes_recorded_only_when_generating(settings, prompt_set):
    """skills.jsonl records a skill only once it generated something this run;
    a fully cached run leaves the record untouched."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills[:1], prompt_set)
    assert load_hashes(settings) == {skills[0].id: skills[0].hash}

    # a run that generates nothing rewrites nothing
    before = index_path(settings).read_text(encoding="utf-8")
    await run_all(FakeLLM(), settings, skills[:1], prompt_set)
    assert index_path(settings).read_text(encoding="utf-8") == before


async def test_skill_md_is_read_only_for_skills_that_generate(settings, prompt_set):
    """A skill's source is read from the snapshot when it is first needed: a run
    whose prompts are all cached never reads it."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    # a skill with a missing prompt but no source in the snapshot generates nothing
    prompt_result_path(settings, skills[0].id, "tagline").unlink()
    skill_md_path(settings, skills[0]).unlink()
    record, _ = await run_one(FakeLLM(), settings, prompt_set, skills[0])
    assert "tagline" not in record["intros"]


async def test_skill_without_skill_md_in_the_snapshot_is_skipped(settings, prompt_set):
    """A skill the snapshot has no SKILL.md for is skipped instead of failing the run."""
    orphan = load_skills(settings)[0].model_copy(update={"id": "owner-x/repo-x/nope"})
    record, _ = await run_one(FakeLLM(), settings, prompt_set, orphan)
    assert record["intros"] == {}  # nothing generated, so nothing cached either
    assert not skill_result_dir(settings, orphan.id).exists()
    assert orphan.id not in load_hashes(settings)


async def test_only_runs_write_no_hash_when_fully_cached(settings, prompt_set):
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    await run_all(FakeLLM(), settings, skills, prompt_set, only={"tagline"})
    # nothing was generated, so no new hashes were recorded
    assert len(load_hashes(settings)) == 4


async def test_run_trusts_existing_outputs_invalidated_by_sync(settings, prompt_set):
    """Invalidation is sync's job (it prunes stale artifacts); run never re-checks hashes."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    # simulate an upstream update that sync has not pruned yet
    data_file = settings.data_dir / "skills.jsonl"
    entries = [json.loads(line) for line in data_file.read_text(encoding="utf-8").splitlines()]
    for e in entries:
        if e["id"] == "owner-a/repo-a/alpha":
            e["hash"] = "new" + "a" * 61
    data_file.write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
    )

    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, load_skills(settings), prompt_set)
    assert llm.calls == 0  # run trusts per-prompt jsons as-is


async def test_only_reuses_cached_targets_like_a_full_run(settings, prompt_set):
    """`only` follows the same cache rules as a full run: nothing missing -> skip."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    llm = CountingLLM(FakeLLM())
    results = await run_all(llm, settings, skills, prompt_set, only={"tagline"})
    assert llm.calls == 0  # every tagline is already cached
    assert len(results) == 4


async def test_only_fills_in_missing_prompt_and_carries_over_rest(settings, prompt_set):
    """`only` generates just the missing prompt; everything else is carried over."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    # drop Alpha's tagline json to simulate a missing prompt
    tagline_path = prompt_result_path(settings, skills[0].id, "tagline")
    tagline_path.unlink()
    before = stored_outputs(settings, skills[0].id)

    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, skills, prompt_set, only={"tagline"})
    assert llm.calls == 1  # only Alpha's missing tagline was generated

    updated = stored_outputs(settings, skills[0].id)
    assert set(updated) == set(before) | {"tagline"}  # complete again
    for pid, out in before.items():
        assert updated[pid] == out  # carried over untouched


async def test_only_generates_just_the_selected_prompt(settings, prompt_set):
    """With no stored results, `only` runs just the closure of the selection
    (`comments` depends on nothing, so its closure is itself)."""
    skills = load_skills(settings)
    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, skills[:1], prompt_set, only={"comments"})
    assert llm.calls == 1
    assert set(stored_outputs(settings, skills[0].id)) == {"comments"}

    # a partial directory must not count as complete: a full run fills in the gaps
    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, skills[:1], prompt_set)
    assert llm.calls == len(prompt_set.by_id) - 1  # every other prompt was missing
    assert len(stored_outputs(settings, skills[0].id)) == len(prompt_set.by_id)


async def test_invalidated_prompt_regenerates_only_itself(settings, prompt_set):
    """Dropping one prompt's cache makes the next run redo exactly that prompt;
    its dependencies are inputs and keep the normal cache rules."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)
    before = stored_outputs(settings, skills[0].id)

    assert invalidate(settings, [skills[0].id], {"tagline"}) == 1
    # a partially invalidated skill stays on record
    assert skills[0].id in load_hashes(settings)

    # tagline has no dependency, and only tagline was invalidated -> 1 call
    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, skills[:1], prompt_set, only={"tagline"})
    assert llm.calls == 1

    # every other prompt is reused unchanged
    assert len(stored_outputs(settings, skills[0].id)) == len(prompt_set.by_id)
    updated = stored_outputs(settings, skills[0].id)
    for pid in set(prompt_set.by_id) - {"tagline"}:
        assert updated[pid] == before[pid]


async def test_run_preserves_prompts_outside_closure(settings, prompt_set):
    """A run never touches prompts outside the closure: their files survive intact."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)
    before = stored_outputs(settings, skills[0].id)

    # scenario depends on nothing, so its closure is itself: 1 invalidated -> 1 call
    invalidate(settings, [skills[0].id], {"scenario"})
    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, skills[:1], prompt_set, only={"scenario"})
    assert llm.calls == 1
    updated = stored_outputs(settings, skills[0].id)
    assert len(updated) == len(prompt_set.by_id)
    for pid in set(prompt_set.by_id) - {"scenario"}:
        assert updated[pid] == before[pid]


async def test_regenerates_cached_output_failing_current_schema(settings, prompt_set):
    """A cached output that no longer validates (e.g. after a taxonomy change)
    counts as missing and is regenerated instead of crashing the run."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills, prompt_set)

    # rewrite Alpha's stored domain to a value the current enum rejects
    domain_path = prompt_result_path(settings, skills[0].id, "domain")
    domain = json.loads(domain_path.read_text(encoding="utf-8"))
    domain["domain"] = "项目管理"
    domain_path.write_text(json.dumps(domain, ensure_ascii=False), encoding="utf-8")
    before = stored_outputs(settings, skills[0].id)

    llm = CountingLLM(FakeLLM())
    await run_all(llm, settings, skills, prompt_set, only={"domain"})
    assert llm.calls == 1  # only Alpha's stale domain regenerated

    updated = stored_outputs(settings, skills[0].id)
    assert updated["domain"]["domain"] == "办公效率"  # FakeLLM's fixed value
    for pid, out in before.items():
        if pid != "domain":
            assert updated[pid] == out  # carried over untouched


async def test_run_one_rejects_unknown_only(settings, prompt_set):
    skills = load_skills(settings)
    with pytest.raises(KeyError):
        await run_all(FakeLLM(), settings, skills[:1], prompt_set, only={"nope"})


async def test_run_all_isolates_skill_failures(settings, prompt_set):
    """One skill's LLM failure (quota, connection) does not abort the run:
    the other skills still generate, the failure is tallied, the index records
    only the healthy skills, and the failed skill stays fully pending."""
    skills = load_skills(settings)
    stats = RunStats(selected=len(skills))
    records = await run_all(FailingForAlpha(), settings, skills, prompt_set, stats=stats)

    assert stats.skills_failed == 1
    assert stats.skills_generated == 3
    assert [r.get("failed") for r in records].count(True) == 1

    assert set(load_hashes(settings)) == {s.id for s in skills[1:]}
    assert stored_outputs(settings, skills[0].id) == {}


async def test_crash_mid_run_keeps_completed_prompts(settings, prompt_set):
    """Each prompt is committed to disk right after generation, so a crash
    (simulated here by an LLM failing partway) keeps completed prompts and a
    rerun only regenerates what is missing."""
    skills = load_skills(settings)
    skill = skills[0]
    prompts = len(prompt_set.by_id)

    class FlakyLLM:
        """Generates the first two prompts, then explodes."""

        def __init__(self):
            self.inner = FakeLLM()
            self.calls = 0

        async def create(self, response_model=None, messages=None, **kwargs):
            self.calls += 1
            if self.calls > 2:
                raise RuntimeError("boom")
            return await self.inner.create(response_model, messages, **kwargs)

    with pytest.raises(RuntimeError, match="boom"):
        await run_one(FlakyLLM(), settings, prompt_set, skill)
    assert len(stored_outputs(settings, skill.id)) == 2  # first two prompts survived

    llm = CountingLLM(FakeLLM())
    await run_one(llm, settings, prompt_set, skill)  # cache rules apply
    assert llm.calls == prompts - 2  # only the prompts still missing were regenerated
    assert len(stored_outputs(settings, skill.id)) == len(prompt_set.by_id)


async def test_coverage_counts_complete_and_remaining_skills(settings, prompt_set):
    """coverage() applies the run's cache rules dataset-wide: profiled skills
    (text only) and complete ones (text + cover), how many still owe work, and a
    cached count per prompt."""
    skills = load_skills(settings)
    cov = coverage(settings, prompt_set, skills)
    assert cov == {"skills": 4, "profiled": 0, "complete": 0, "remaining": 4,
                   "prompts": {p: 0 for p in prompt_set.by_id}}

    # text alone profiles a skill; only the cover makes it complete
    await run_all(FakeLLM(), settings, skills[:2], prompt_set)
    cov = coverage(settings, prompt_set, skills)
    assert (cov["profiled"], cov["complete"], cov["remaining"]) == (2, 0, 4)

    await complete(settings, prompt_set, skills[:2])
    cov = coverage(settings, prompt_set, skills)
    assert (cov["profiled"], cov["complete"], cov["remaining"]) == (2, 2, 2)
    assert all(n == 2 for n in cov["prompts"].values())

    # only counts the selected prompts' closure
    cov = coverage(settings, prompt_set, skills, only={"tagline"})
    assert cov["prompts"] == {"tagline": 2}


async def test_coverage_matches_run_cache_rules(settings, prompt_set):
    """A schema-stale output is not coverage-cached, same as a run regenerates it."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills[:1], prompt_set)
    domain_path = prompt_result_path(settings, skills[0].id, "domain")
    domain = json.loads(domain_path.read_text(encoding="utf-8"))
    domain["domain"] = "项目管理"
    domain_path.write_text(json.dumps(domain, ensure_ascii=False), encoding="utf-8")

    cov = coverage(settings, prompt_set, skills[:1])
    assert cov["complete"] == 0  # the stale domain makes the skill incomplete
    assert cov["prompts"]["domain"] == 0


async def test_run_all_tallies_stats(settings, prompt_set):
    """run_all folds generated/reused/stale counters and LLM seconds into RunStats."""
    skills = load_skills(settings)

    stats = RunStats()
    await run_all(FakeLLM(), settings, skills, prompt_set, stats=stats)
    assert stats.selected == 0  # the caller sets it; run_all only tallies records
    assert stats.skills_generated == 4
    assert stats.prompts_generated == 4 * len(prompt_set.by_id)
    assert stats.prompts_reused == 0
    assert stats.prompts_stale == 0
    assert stats.llm_seconds > 0

    stats = RunStats()
    await run_all(FakeLLM(), settings, skills, prompt_set, stats=stats)
    assert stats.skills_generated == 0
    assert stats.prompts_generated == 0
    assert stats.prompts_reused == 4 * len(prompt_set.by_id)
    assert stats.llm_seconds == 0.0


async def test_prompts_within_a_skill_share_the_concurrency_pool(settings, prompt_set):
    """Independent prompts of one skill run in parallel, bounded by the shared pool;
    the per-skill record separates wall time from summed LLM seconds."""
    settings.concurrency = 8  # standalone run_one bounds itself by settings
    skill = load_skills(settings)[0]
    llm = ConcurrencyTrackingLLM(FakeLLM())
    record, reused = await run_one(llm, settings, prompt_set, skill)
    assert not reused
    assert llm.peak == 7  # all seven prompts are roots and fan out at once
    assert set(record["prompt_seconds"]) == set(record["generated"])

    # the same pool caps skills and prompts together: another skill, concurrency 2
    settings.concurrency = 2
    llm = ConcurrencyTrackingLLM(FakeLLM())
    await run_all(llm, settings, load_skills(settings)[1:2], prompt_set)
    assert llm.peak == 2


async def test_run_one_standalone_gets_its_own_pool(settings, prompt_set):
    """Without a shared semaphore, run_one bounds itself by settings.concurrency."""
    settings.concurrency = 3
    skill = load_skills(settings)[0]
    llm = ConcurrencyTrackingLLM(FakeLLM())
    await run_one(llm, settings, prompt_set, skill)
    assert llm.peak == 3


async def test_run_stats_count_stale_caches(settings, prompt_set):
    """A cached output failing the current schema is regenerated and counted stale."""
    skills = load_skills(settings)
    await run_all(FakeLLM(), settings, skills[:1], prompt_set)
    domain_path = prompt_result_path(settings, skills[0].id, "domain")
    domain = json.loads(domain_path.read_text(encoding="utf-8"))
    domain["domain"] = "项目管理"
    domain_path.write_text(json.dumps(domain, ensure_ascii=False), encoding="utf-8")

    stats = RunStats()
    await run_all(FakeLLM(), settings, skills[:1], prompt_set, stats=stats)
    assert stats.prompts_generated == 1
    assert stats.prompts_stale == 1
    assert stats.prompts_reused == len(prompt_set.by_id) - 1


async def test_run_stats_count_skills_without_source(settings, prompt_set):
    """A skill the snapshot has no SKILL.md for lands in skills_skipped."""
    skills = load_skills(settings)
    orphan = skills[0].model_copy(update={"id": "owner-x/repo-x/nope"})
    stats = RunStats()
    await run_all(FakeLLM(), settings, [orphan], prompt_set, stats=stats)
    assert stats.skills_skipped == 1
    assert stats.skills_generated == 0


async def test_dep_outputs_flow_into_downstream_prompts(settings, tmp_path):
    """A dependent prompt's rendered user message carries its deps' parsed output."""
    (tmp_path / "_system.md").write_text("system prompt", encoding="utf-8")
    (tmp_path / "scenario.md").write_text(
        "---\noutput: IntroText\n---\n场景化介绍", encoding="utf-8"
    )
    (tmp_path / "comments.md").write_text(
        "---\noutput: SkillComments\ndepends_on: [scenario]\n---\n"
        "基于这段介绍写评论: {{ deps.scenario.text }}", encoding="utf-8"
    )
    prompts = load_prompt_set(tmp_path)
    seen_messages = []

    class RecordingLLM:
        async def create(self, response_model=None, messages=None, **kwargs):
            seen_messages.append(messages[-1]["content"])
            return await FakeLLM().create(response_model, messages, **kwargs)

    await run_one(RecordingLLM(), settings, prompts, load_skills(settings)[0])
    assert any("离线演示档案文本" in m for m in seen_messages)  # scenario flows in via deps


async def test_model_and_system_prompt_passed_to_llm(settings, prompt_set):
    skill = load_skills(settings)[0]
    seen = {}

    class RecordingLLM:
        async def create(self, response_model=None, messages=None, **kwargs):
            seen[response_model.__name__] = (kwargs, messages)
            return await FakeLLM().create(response_model, messages, **kwargs)

    await run_one(RecordingLLM(), settings, prompt_set, skill)
    expected = {spec.output_model.__name__ for spec in prompt_set.by_id.values()}
    assert set(seen) == expected
    for kwargs, _ in seen.values():
        assert kwargs["model"] == settings.model
    # every skill-context prompt carries the same system message: sales framing
    # + SKILL.md; cover (use_system: false) runs user-only
    for _, messages in seen.values():
        assert messages[-1]["role"] == "user"
    cover = seen["ImagePrompt"]
    assert [m["role"] for m in cover[1]] == ["user"]


async def test_cover_prompt_skips_system_prompt(settings, prompt_set):
    """use_system: false in cover.md keeps its call self-contained: user-only,
    no SKILL.md, no sales framing — a translation task needs neither."""
    skill = load_skills(settings)[0]
    seen = {}

    class RecordingLLM:
        async def create(self, response_model=None, messages=None, **kwargs):
            seen[response_model.__name__] = messages
            return await FakeLLM().create(response_model, messages, **kwargs)

    await run_one(RecordingLLM(), settings, prompt_set, skill)
    assert [m["role"] for m in seen["ImagePrompt"]] == ["user"]
    assert "Alpha does useful things" not in seen["ImagePrompt"][0]["content"]


async def test_rate_limited_llm_is_transparent(settings, prompt_set):
    """The RPM wrapper passes calls through untouched; a limiter is the only
    thing it adds, so a rate of 0 degrades to the plain inner client."""
    skill = load_skills(settings)[0]
    llm = RateLimitedLLM(FakeLLM(), rate=0)
    outputs, _ = await run_one(llm, settings, prompt_set, skill)
    assert not outputs.get("skipped") and not outputs.get("failed")
    assert outputs["intros"]


async def test_regenerated_cover_drops_its_stale_picture(settings, prompt_set):
    """A regenerated recipe must not sit next to the picture of the old one:
    the asset dies with the output that produced it, or the render pass would
    keep a cover.png that matches nothing on disk."""
    skill = load_skills(settings)[0]
    skill_dir = skill_result_dir(settings, skill.id)
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "persona.json").write_text(
        json.dumps({"tool": "扳手", "pitch": "x"}), encoding="utf-8")
    (skill_dir / "cover.json").write_text(
        json.dumps({"text": "a sturdy chrome wrench"}), encoding="utf-8")  # no "one " prefix
    (skill_dir / "cover.png").write_bytes(b"stale picture")

    record, _ = await run_one(FakeLLM(), settings, prompt_set, skill)

    assert not (skill_dir / "cover.png").exists(), "stale picture survived its recipe"
    assert json.loads((skill_dir / "cover.json").read_text(encoding="utf-8"))["text"] \
        .startswith("one ")
    assert record["stale"] == ["cover"]


async def test_fully_cached_skill_keeps_its_picture(settings, prompt_set):
    """A skill with valid outputs and its render keeps both: the invalidation
    on regeneration only fires when something is actually regenerated."""
    skill = load_skills(settings)[0]
    await complete(settings, prompt_set, [skill])
    png = skill_result_dir(settings, skill.id) / "cover.png"
    before = png.read_bytes()

    record, reused = await run_one(FakeLLM(), settings, prompt_set, skill)

    assert reused
    assert "generated" not in record
    assert png.read_bytes() == before


async def test_selecting_and_reporting_never_touch_the_disk(settings, prompt_set):
    """Selecting skills and reporting coverage apply the run's cache rules without
    deleting anything: the invalidation a regeneration implies is `run_one`'s job,
    so a skill the budget never reaches keeps its files exactly as they were."""
    skill = load_skills(settings)[0]
    skill_dir = skill_result_dir(settings, skill.id)
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "persona.json").write_text('{"tool": 42}', encoding="utf-8")  # invalid
    (skill_dir / "cover.json").write_text('{"text": "one chrome wrench"}', encoding="utf-8")
    picture = skill_dir / "cover.png"
    picture.write_bytes(b"the picture of the old recipe")

    assert [s.id for s in select_skills(settings, prompt_set, [skill], limit=1)] == [skill.id]
    coverage(settings, prompt_set, [skill])

    assert (skill_dir / "cover.json").is_file(), "reading must not drop what it only planned"
    assert picture.read_bytes() == b"the picture of the old recipe"
    assert not index_path(settings).exists(), "nothing was generated, so nothing was recorded"

    # generating is what applies the plan: the persona is redone, and the cover
    # recipe plus the picture of the old one go with it
    record, _ = await run_one(FakeLLM(), settings, prompt_set, skill)
    assert {"persona", "cover"} <= set(record["generated"])
    assert record["stale"] == ["persona"]
    assert not picture.exists()


async def test_debug_dumps_rendered_messages(settings, prompt_set, capfd):
    """debug=True prints the exact system/user messages to stderr before each call."""
    skill = load_skills(settings)[0]
    await run_one(FakeLLM(), settings, prompt_set, skill, debug=True)

    err = capfd.readouterr().err
    assert f"===== debug {skill.id} / domain =====" in err
    assert "----- system -----" in err
    assert "----- user -----" in err
    assert "Alpha does useful things." in err  # rendered skill_md, not the raw template
